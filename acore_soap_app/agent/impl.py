# -*- coding: utf-8 -*-

"""
todo: add docstring
"""

import typing as T
import dataclasses
import xml.etree.ElementTree as ET

import requests
from ..paths import dir_python_lib

path_xml = dir_python_lib.joinpath("agent", "execute-command.xml")
execute_command_xml = path_xml.read_text(encoding="utf-8")


@dataclasses.dataclass
class SoapResponse:
    """
    Parse SOAP XML response.

    Usage:

    .. code-block:: python

        >>> res = SoapResponse.parse("<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope ... </SOAP-ENV:Envelope>")
    """

    body: str = dataclasses.field()
    message: str = dataclasses.field()
    succeeded: bool = dataclasses.field()

    @classmethod
    def parse(cls, body: str) -> "SoapResponse":
        """
        Parse the response from SOAP.
        """
        root = ET.fromstring(body)
        results = list(root.iter("result"))
        if len(results):
            return cls(
                body=body,
                message=results[0].text,
                succeeded=True,
            )
        faultstrings = list(root.iter("faultstring"))
        if len(faultstrings):
            return cls(
                body=body,
                message=faultstrings[0].text,
                succeeded=False,
            )

        raise ValueError("Cannot parse the response")


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
