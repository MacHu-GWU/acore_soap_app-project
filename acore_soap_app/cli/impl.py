# -*- coding: utf-8 -*-

import typing as T
import json

from ..agent.api import SOAPRequest, SOAPResponse, get_boto_ses
from ..exc import SOAPCommandFailedError
from ..utils import get_object, put_object


def ensure_ec2_environment():
    if not __file__.startswith("/home/ubuntu"):
        raise EnvironmentError("This is not a EC2 environment")


def ensure_response_succeeded(
    request: SOAPRequest,
    response: SOAPResponse,
    raises: bool,
) -> SOAPResponse:
    if response.succeeded:
        return response
    else:
        if raises:
            raise SOAPCommandFailedError(
                f"request failed: {request.command!r}, "
                f"response: {response.message!r}"
            )
        else:
            return response


def gm(
    request: T.Union[str, SOAPRequest],
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
    raises: bool = True,
    s3uri_output: T.Optional[str] = None,
):
    """
    运行一个 GM 命令, 例如 ``.server info``.

    :param request: 如果是 :class:`~acore_soap_app.agent.impl.SOAPRequest` 对象,
        那么就直接发送该请求. 如果是一个字符串, 则将其视为一个 S3 URI, 到 S3 上读取请求
        对象数据. 常用于请求特别大的情况.
    :param username: 默认的用户名, 只有当 request.username 为 None 的时候才会用到.
    :param password: 默认的密码, 只有当 request.password 为 None 的时候才会用到.
    :param raises: 默认为 True. 如果为 True, 则在遇到错误时抛出异常. 反之则将
        failed SOAP Response 原封不动地返回.
    :param s3uri_output: 可选参数, 如果为 None, 则将
        :class:`~acore_soap_app.agent.impl.SOAPResponse` 对象转换为 JSON 并打印.
        如果给定, 则将 JSON 保存到 S3 中. 常用于返回结果特别大的情况.
    """
    ensure_ec2_environment()
    s3_client = None

    # handle input
    if isinstance(request, str):
        boto_ses = get_boto_ses()
        s3_client = boto_ses.client("s3")
        request = SOAPRequest.from_json(get_object(s3_client, s3uri=request))
    request.set_default(username=username, password=password)

    # run
    response = ensure_response_succeeded(request, request.send(), raises=raises)

    # handle output
    if s3uri_output is None:
        print(response.to_json())
    else:
        if s3_client is None:
            boto_ses = get_boto_ses()
            s3_client = boto_ses.client("s3")
        put_object(s3_client, s3uri=s3uri_output, body=response.to_json())


def batch_gm(
    requests: T.Union[str, T.Iterable[SOAPRequest]],
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
    raises: bool = True,
    s3uri_output: T.Optional[str] = None,
):
    """
    按顺序运行一批 GM 命令.

    :param requests: 一批 :class:`~acore_soap_app.agent.impl.SOAPRequest` 对象.
    :param username: 默认的用户名, 只有当 request.username 为 None 的时候才会用到.
    :param password: 默认的密码, 只有当 request.password 为 None 的时候才会用到.
    :param raises: 默认为 True. 如果为 True, 则在遇到错误时抛出异常. 反之则将
        failed SOAP Response 原封不动地返回.
    :param s3uri_output: 可选参数, 如果为 None, 则将
        :class:`~acore_soap_app.agent.impl.SOAPResponse` 对象转换为 JSON 并打印.
        如果给定, 则将 JSON 保存到 S3 中. 常用于返回结果特别大的情况.
    """
    ensure_ec2_environment()
    s3_client = None

    # handle input
    if isinstance(requests, str):
        boto_ses = get_boto_ses()
        s3_client = boto_ses.client("s3")
        json_str = get_object(s3_client, s3uri=requests)
        requests = [SOAPRequest.from_dict(dct) for dct in json.loads(json_str)]
    for request in requests:
        request.set_default(username=username, password=password)

    # run
    responses = [
        ensure_response_succeeded(request, request.send(), raises)
        for request in requests
    ]

    # handle output
    if s3uri_output is None:
        print("\n".join([response.to_json() for response in responses]))
    else:
        if s3_client is None:
            boto_ses = get_boto_ses()
            s3_client = boto_ses.client("s3")
        put_object(
            s3_client,
            s3uri=s3uri_output,
            body=json.dumps([response.to_dict() for response in responses]),
        )


# def remote_gm(
#     server_id: str,
#     cmd: str,
#     username: str = "admin",
#     password: str = "admin",
#     region: T.Optional[str] = None,
#     profile: T.Optional[str] = None,
#     delays: int = 1,
#     timeout: int = 10,
#     verbose: bool = True,
# ):
#     """
#     Example: acsoap gm ".server info"
#     """
#     bsm = BotoSesManager(region_name=region, profile_name=profile)
#     soap_res = run_remote_soap_command(
#         bsm=bsm,
#         server_id=server_id,
#         cmd=cmd,
#         username=username,
#         password=password,
#         sync=True,
#         delays=delays,
#         timeout=timeout,
#         verbose=verbose,
#     )
#     print(soap_res.to_json())
