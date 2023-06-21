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

# ------------------------------------------------------------------------------
# Soap Request and Response
# ------------------------------------------------------------------------------
path_xml = dir_python_lib.joinpath("agent", "execute-command.xml")

# default soap request headers
_SOAP_REQUEST_HEADERS = {"Content-Type": "application/xml"}
_SOAP_REQUEST_XML_TEMPLATE = path_xml.read_text(encoding="utf-8")
_DEFAULT_USERNAME = "admin"
_DEFAULT_PASSWORD = "admin"
_DEFAULT_HOST = "localhost"
_DEFAULT_PORT = 7878


@dataclasses.dataclass
class Base:
    @classmethod
    def from_dict(cls, dct: dict):
        """
        Construct an object from a dict.
        """
        return cls(**dct)

    def to_dict(self) -> dict:
        """
        Convert the object to a dict.
        """
        return dataclasses.asdict(self)

    @classmethod
    def from_json(cls, json_str: str):
        """
        Construct an object from a JSON string.
        """
        return cls.from_dict(json.loads(json_str))

    def to_json(self) -> str:  # pragma: no cover
        """
        Convert the object to a JSON string.
        """
        return json.dumps(self.to_dict())


@dataclasses.dataclass
class SOAPRequest(Base):
    """
    :class:`~acore_soap_app.agent.impl.SOAPRequest` is a dataclass to represent
    the SOAP XML request.

    Usage example

    .. code-block:: python

        # this code only works in EC2 environment
        >>> request = SOAPRequest(command=".server info")
        >>> response = request.send()
        >>> response.to_json()
        {
            "body": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:SOAP-ENC=\"http://schemas.xmlsoap.org/soap/encoding/\" xmlns:xsi=\"http://www.w3.org/1999/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/1999/XMLSchema\" xmlns:ns1=\"urn:AC\"><SOAP-ENV:Body><ns1:executeCommandResponse><result>AzerothCore rev. 85311fa55983 2023-03-25 22:36:05 +0000 (master branch) (Unix, RelWithDebInfo, Static)&#xD;\nConnected players: 0. Characters in world: 0.&#xD;\nConnection peak: 0.&#xD;\nServer uptime: 54 minute(s) 3 second(s)&#xD;\nUpdate time diff: 10ms, average: 10ms.&#xD;\n</result></ns1:executeCommandResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>",
            "message": "AzerothCore rev. 85311fa55983 2023-03-25 22:36:05 +0000 (master branch) (Unix, RelWithDebInfo, Static)\r\nConnected players: 0. Characters in world: 0.\r\nConnection peak: 0.\r\nServer uptime: 54 minute(s) 3 second(s)\r\nUpdate time diff: 10ms, average: 10ms.",
            "succeeded": true
        }

    :param command: the command to execute.
    :param username: the in game GM account username, default "admin".
    :param password: the in game GM account password, default "admin".
    :param host: wow world server host, default "localhost".
    :param port: wow world server SOAP port, default 7878.
    """

    command: str = dataclasses.field()
    username: str = dataclasses.field(default=_DEFAULT_USERNAME)
    password: str = dataclasses.field(default=_DEFAULT_PASSWORD)
    host: str = dataclasses.field(default=_DEFAULT_HOST)
    port: int = dataclasses.field(default=_DEFAULT_PORT)

    @property
    def endpoint(self) -> str:
        """
        Construct the Soap service endpoint URL.
        """
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}/"

    def send(self) -> "SOAPResponse":  # pragma: no cover
        """
        Run soap command via HTTP request. This function "has to" be run on the
        game server and talk to the localhost. You should NEVER open SOAP port
        to public!
        """
        http_response = requests.post(
            self.endpoint,
            headers=_SOAP_REQUEST_HEADERS,
            data=_SOAP_REQUEST_XML_TEMPLATE.format(command=self.command),
        )
        return SOAPResponse.parse(http_response.text)


@dataclasses.dataclass
class SOAPResponse(Base):
    """
    :class:`~acore_soap_app.agent.impl.SOAPResponse` is a dataclass to represent
    the SOAP XML response.

    Usage:

    .. code-block:: python

        >>> res = SOAPResponse.parse(
        ...  '''
        ...      <?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope
        ...      ...<result>Account created: test&#xD;</result>...</SOAP-ENV:Envelope>
        ...  '''
        ... )
        >>> res.message
        Account created: test
        >>> res.succeeded
        True

    :param body: the raw SOAP XML response
    :param message: if succeeded, it is the ``<result>...</result>`` part.
        if failed, it is the ``<faultstring>...</faultstring>`` part
    :param succeeded: a boolean flag to indicate whether the command is succeeded
    """

    body: str = dataclasses.field()
    message: str = dataclasses.field()
    succeeded: bool = dataclasses.field()

    @classmethod
    def parse(cls, body: str) -> "SOAPResponse":
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

    def print(self):  # pragma: no cover
        """
        Print the dataclass, ignore the raw response body.
        """
        print({"succeeded": self.succeeded, "message": self.message})


# ------------------------------------------------------------------------------
# Create boto3 session on EC2
# ------------------------------------------------------------------------------
def get_ec2_metadata(name: str) -> str:  # pragma: no cover
    """
    Get the EC2 instance id from the AWS EC2 metadata API.

    Reference:

    - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
    """
    url = f"http://169.254.169.254/latest/meta-data/{name}"
    return requests.get(url).text.strip()


def get_ec2_region() -> str:  # pragma: no cover
    return get_ec2_metadata("placement/region")


def get_boto_ses() -> boto3.session.Session:  # pragma: no cover
    """
    On EC2, we use the IAM role to get the AWS credentials. You only need to
    specify the region name, however, it is automatically discovered by the
    EC2 metadata API.
    """
    return boto3.session.Session(region_name=get_ec2_region())
