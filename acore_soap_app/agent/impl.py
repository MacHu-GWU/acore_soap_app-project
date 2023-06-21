# -*- coding: utf-8 -*-

"""
Agent implementation.
"""

import typing as T
import json
import dataclasses
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

import boto3
import requests

from ..paths import dir_python_lib
from ..exc import SOAPResponseParseError
from ..utils import get_object, put_object


# ------------------------------------------------------------------------------
# Soap Request and Response
# ------------------------------------------------------------------------------
path_xml = dir_python_lib.joinpath("agent", "execute-command.xml")

# default soap request headers
_SOAP_REQUEST_HEADERS = {"Content-Type": "application/xml"}
_SOAP_REQUEST_XML_TEMPLATE = path_xml.read_text(encoding="utf-8")
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 7878


@dataclasses.dataclass
class Base:
    """
    Base class for :class:`SOAPRequest` and :class:`SOAPResponse`.
    """
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
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}

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

    @classmethod
    def batch_load_from_s3(
        cls,
        s3_client,
        s3uri: str,
    ):
        """
        从 S3 中加载多个对象.
        """
        json_str = get_object(s3_client, s3uri=s3uri)
        return [cls.from_dict(dct) for dct in json.loads(json_str)]

    @classmethod
    def batch_dump_to_s3(
        cls,
        s3_client,
        instances: T.Iterable,
        s3uri: str,
    ):
        """
        将多个对象以 JSON 格式保存到 S3 中.
        """
        data = [instance.to_dict() for instance in instances]
        put_object(s3_client=s3_client, s3uri=s3uri, body=json.dumps(data))


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
            "body": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:SOAP-ENC=\"http://schemas.xmlsoap.org/soap/encoding/\" xmlns:xsi=\"http://www.w3.org/1999/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/1999/XMLSchema\" xmlns:ns1=\"urn:AC\"><SOAP-ENV:Body><ns1:executeCommandResponse><result>AzerothCore rev. 85311fa55983 2023-03-25 22:36:05 +0000 (master branch) (Unix, RelWithDebInfo, Static)&#xD;Connected players: 0. Characters in world: 0.&#xD;Connection peak: 0.&#xD;Server uptime: 54 minute(s) 3 second(s)&#xD;Update time diff: 10ms, average: 10ms.&#xD;</result></ns1:executeCommandResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>",
            "message": "AzerothCore rev. 85311fa55983 2023-03-25 22:36:05 +0000 (master branch) (Unix, RelWithDebInfo, Static)Connected players: 0. Characters in world: 0.Connection peak: 0.Server uptime: 54 minute(s) 3 second(s)Update time diff: 10ms, average: 10ms.",
            "succeeded": true
        }

    :param command: the command to execute.
    :param username: the in game GM account username, default "admin".
    :param password: the in game GM account password, default "admin".
    :param host: wow world server host, default "localhost".
    :param port: wow world server SOAP port, default 7878.

    More methods from base class:

    - :meth:`~Base.from_dict`
    - :meth:`~Base.to_dict`
    - :meth:`~Base.from_json`
    - :meth:`~Base.to_json`
    - :meth:`~Base.batch_load_from_s3`
    - :meth:`~Base.batch_dump_to_s3`
    """

    command: str = dataclasses.field()
    username: T.Optional[str] = dataclasses.field(default=None)
    password: T.Optional[str] = dataclasses.field(default=None)
    host: T.Optional[str] = dataclasses.field(default=None)
    port: T.Optional[int] = dataclasses.field(default=None)

    def set_default(
        self,
        username: T.Optional[str],
        password: T.Optional[str],
    ):
        """
        Set default values for username and password if they are not set.
        """
        if self.username is None:
            self.username = username
        if self.password is None:
            self.password = password

    @property
    def endpoint(self) -> str:
        """
        Construct the Soap service endpoint URL.
        """
        username = self.username or DEFAULT_USERNAME
        password = self.password or DEFAULT_PASSWORD
        host = self.host or DEFAULT_HOST
        port = self.port or DEFAULT_PORT
        return f"http://{username}:{password}@{host}:{port}/"

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

    @classmethod
    def batch_load(
        cls,
        request_like: T.Union[
            str,
            T.List[str],
            "SOAPRequest",
            T.List["SOAPRequest"],
        ],
        username: T.Optional[str] = None,
        password: T.Optional[str] = None,
        s3_client=None,
    ) -> T.List["SOAPRequest"]:
        """
        从各种形式的输入中加载 :class:`SOAPRequest`. 该方法总是返回一个列表.

        输入参数 ``request_like`` 代表着要运行的 GM 命令, 它可能是以下几种形式中的一种:

        - 如果是一个字符串:
            - 如果是以 s3:// 开头, 那么就去 S3 读数据, 此时需要给定 ``s3_client`` 参数.
                通常用于 payload 比较大的情况:
                - 如果读到的数据是单个字典, 那么就视为一个 SOAPRequest.
                - 如果读到的数据是一个列表, 那么就视为多个 SOAPRequest.
            - 如果不是以 s3:// 开头, 那么就视为一个 GM command.
        - 如果是一个字符串列表, 那么就视为多个 GM 命令.
        - 它还可以是单个 SOAPRequest 或 SOAPRequest 列表.
        - 这个参数最终都会被转换成 SOAPRequest 的列表.

        :param request_like: 上面已经说过了.
        :param username: 默认的用户名, 只有当 request.username 为 None 的时候才会用到.
        :param password: 默认的密码, 只有当 request.password 为 None 的时候才会用到.
        :param s3_client: boto3.client("s3")
        """
        if isinstance(request_like, str):
            if request_like.startswith("s3://"):  # pragma: no cover
                data = json.loads(get_object(s3_client=s3_client, s3uri=request_like))
                if isinstance(data, dict):  # pragma: no cover
                    requests = [SOAPRequest.from_dict(data)]
                elif isinstance(data, list):
                    requests = [SOAPRequest.from_dict(dct) for dct in data]
                else:  # pragma: no cover
                    raise TypeError(
                        f"data in S3 must be a dict or "
                        f"a list of dict, not {type(data)}"
                    )
            else:
                requests = [SOAPRequest(command=request_like)]
        elif isinstance(request_like, SOAPRequest):
            requests = [request_like]
        elif isinstance(request_like, list):
            if isinstance(request_like[0], str):
                requests = [SOAPRequest(command=item) for item in request_like]
            elif isinstance(request_like[0], SOAPRequest):
                requests = request_like
            else:
                raise TypeError(
                    f"item ``request_like`` list must be "
                    f"str or SOAPRequest, not {type(request_like[0])}"
                )
        else:  # pragma: no cover
            raise TypeError(
                f"request must be str or SOAPRequest, " f"not {type(request_like)}"
            )
        for request in requests:
            request.set_default(username=username, password=password)
        return requests


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

    More methods from base class:

    - :meth:`~Base.from_dict`
    - :meth:`~Base.to_dict`
    - :meth:`~Base.from_json`
    - :meth:`~Base.to_json`
    - :meth:`~Base.batch_load_from_s3`
    - :meth:`~Base.batch_dump_to_s3`
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

        raise SOAPResponseParseError(f"Cannot parse the response: {body!r}")

    def print(self):  # pragma: no cover
        """
        Print the dataclass, ignore the raw response body.
        """
        print({"succeeded": self.succeeded, "message": self.message})


# ------------------------------------------------------------------------------
# Create boto3 session on EC2
# ------------------------------------------------------------------------------
path_aws_region_cache = Path.home().joinpath(".aws_region_cache.json")


def _dump_aws_region_cache(region: str):  # pragma: no cover
    path_aws_region_cache.write_text(
        json.dumps({"region": region, "timestamp": int(datetime.utcnow().timestamp())})
    )


def _load_aws_region_cache() -> T.Optional[str]:  # pragma: no cover
    if not path_aws_region_cache.exists():
        return None
    data = json.loads(path_aws_region_cache.read_text())
    if (datetime.utcnow().timestamp() - data["timestamp"]) > 86400:  # cache expired
        return None
    else:
        return data["region"]


def get_ec2_metadata(name: str) -> str:  # pragma: no cover
    """
    Get the EC2 instance id from the AWS EC2 metadata API.

    Reference:

    - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
    """
    url = f"http://169.254.169.254/latest/meta-data/{name}"
    return requests.get(url).text.strip()


def get_ec2_region() -> str:  # pragma: no cover
    region = _load_aws_region_cache()
    if region is None:
        region = get_ec2_metadata("placement/region")
        _dump_aws_region_cache(region)
    return region


def get_boto_ses() -> boto3.session.Session:  # pragma: no cover
    """
    On EC2, we use the IAM role to get the AWS credentials. You only need to
    specify the region name, however, it is automatically discovered by the
    EC2 metadata API.
    """
    return boto3.session.Session(region_name=get_ec2_region())
