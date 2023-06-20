# -*- coding: utf-8 -*-

"""
todo: add docstring
"""

import typing as T
import json
import dataclasses
import xml.etree.ElementTree as ET

import boto3
import requests

from ..paths import dir_python_lib
from ..exc import SoapResponseParseError

path_xml = dir_python_lib.joinpath("agent", "execute-command.xml")
execute_command_xml = path_xml.read_text(encoding="utf-8")


@dataclasses.dataclass
class SoapResponse:
    """
    A dataclass to represent the SOAP XML response.

    Usage:

    .. code-block:: python

        >>> res = SoapResponse.parse("<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope ... </SOAP-ENV:Envelope>")

    :param body: the raw SOAP XML response
    :param message: if succeeded, it is the result part. if failed, it is the
        faultstring part
    :param succeeded: a boolean flag to indicate whether the command is succeeded
    """

    body: str = dataclasses.field()
    message: str = dataclasses.field()
    succeeded: bool = dataclasses.field()

    @classmethod
    def parse(cls, body: str) -> "SoapResponse":
        """
        Parse the SOAP XML response.
        """
        root = ET.fromstring(body)
        results = list(root.iter("result"))
        if len(results):
            return cls(
                body=body.strip(),
                message=results[0].text.strip(),
                succeeded=True,
            )
        faultstrings = list(root.iter("faultstring"))
        if len(faultstrings):
            return cls(
                body=body.strip(),
                message=faultstrings[0].text.strip(),
                succeeded=False,
            )

        raise SoapResponseParseError(f"Cannot parse the response: {body!r}")

    def to_dict(self) -> dict:  # pragma: no cover
        """
        Convert the dataclass to a dictionary.
        """
        return dataclasses.asdict(self)

    def to_json(self) -> str:  # pragma: no cover
        """
        Convert the dataclass to a JSON string.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "SoapResponse":  # pragma: no cover
        """
        Construct a dataclass from a JSON string.
        """
        return cls(**json.loads(json_str))

    def print(self):
        """
        Print the dataclass, ignore the raw response body.
        """
        print({"succeeded": self.succeeded, "message": self.message})


def run_soap_command(
    command: str,
    username: str = "admin",
    password: str = "admin",
) -> SoapResponse:  # pragma: no cover
    """
    Run soap command via HTTP request. This function has to be run on the game server
    and talk to the localhost.

    :param command: the command to execute
    :param username: the in game GM account username
    :param username: the in game GM account password

    :return: the result part of the string in xml response. if None,
      means it is failed
    """
    # construct url
    url = f"http://{username}:{password}@localhost:7878/"
    # HTTP headers
    headers = {"Content-Type": "application/xml"}
    # build the final XML request
    xml = path_xml.read_text(encoding="utf-8").format(command=command)
    # send the request
    http_response = requests.post(url, headers=headers, data=xml)
    # parse response
    return SoapResponse.parse(http_response.text)


def get_ec2_metadata(name: str) -> str:  # pragma: no cover
    """
    Get the EC2 instance id from the AWS EC2 metadata API.

    Reference:

    - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
    """
    url = f"http://169.254.169.254/latest/meta-data/{name}"
    return requests.get(url).text.strip()


def get_ec2_region() -> str:
    return get_ec2_metadata("placement/region")


def get_boto_ses() -> boto3.session.Session:
    return boto3.session.Session(region_name=get_ec2_region())
