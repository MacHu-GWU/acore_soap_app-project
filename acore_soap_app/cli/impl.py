# -*- coding: utf-8 -*-

"""
Command line low lever implementations.
"""

import typing as T
import json
from datetime import datetime, timezone

from acore_constants.api import TagKey

from ..agent.api import SOAPRequest, SOAPResponse, get_boto_ses
from ..sdk.api import canned
from ..exc import SOAPCommandFailedError


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
    request_like: T.Union[
        str,
        T.List[str],
        "SOAPRequest",
        T.List["SOAPRequest"],
    ],
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
    raises: bool = True,
    s3uri_output: T.Optional[str] = None,
):
    """
    运行一个或多个 GM 命令. 例如 ``.server info``.

    :param request_like: 请参考 :class:`~acore_soap_app.agent.impl.SOAPRequest.batch_load`
    :param username: 默认的用户名, 只有当 request.username 为 None 的时候才会用到.
    :param password: 默认的密码, 只有当 request.password 为 None 的时候才会用到.
    :param raises: 默认为 True. 如果为 True, 则在遇到错误时抛出异常. 反之则将
        failed SOAP Response 原封不动地返回.
    :param s3uri_output: 可选参数, 如果为 None, 则将
        :class:`~acore_soap_app.agent.impl.SOAPResponse` 对象转换为 JSON 并打印.
        如果给定, 则将 JSON 保存到 S3 中. 常用于返回结果特别大的情况.
    """
    ensure_ec2_environment()

    # handle input
    boto_ses = get_boto_ses()
    s3_client = boto_ses.client("s3")
    requests = SOAPRequest.batch_load(
        request_like=request_like,
        username=username,
        password=password,
        s3_client=s3_client,
    )

    # run
    responses = [
        ensure_response_succeeded(request, request.send(), raises=raises)
        for request in requests
    ]

    # handle output
    if s3uri_output is None:
        print("\n".join([response.to_json() for response in responses]))
    else:
        SOAPResponse.batch_dump_to_s3(
            s3_client=s3_client,
            instances=responses,
            s3uri=s3uri_output,
        )


def _count_online_players(
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
) -> dict:
    """
    底层函数, 通过运行 GM 命令来获得服务器的在线玩家数, 同时获得服务器的在线状态.
    返回一个包含以上信息的字典.

    Example output:

    .. code-block:: python

        {
            "connected_players": 1000,
            "characters_in_world": 700,
            "server_is_online": True,
        }
    """
    requests = SOAPRequest.batch_load(
        request_like=".server info",
        username=username,
        password=password,
    )
    request = requests[0]
    try:
        response = request.send()
        connected_players, characters_in_world = canned.extract_online_players(
            response.message
        )
        return {
            "connected_players": connected_players,
            "characters_in_world": characters_in_world,
            "server_is_online": True,
        }
    except Exception as e:
        return {
            "connected_players": None,
            "characters_in_world": None,
            "server_is_online": False,
        }


def count_online_players(
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
):
    """
    打印在线玩家数量, 以及服务器的在线状态, 以 JSON 的形式输出到 stdout.
    """
    data = _count_online_players(username=username, password=password)
    print(json.dumps(data, indent=4))


def measure_server_status(
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
):
    """
    测量服务器的在线状态, 并将结果保存到 EC2 实例的 Tags 中.
    """
    from boto_session_manager import BotoSesManager
    from simple_aws_ec2.api import Ec2Instance

    data = _count_online_players(username=username, password=password)
    now = datetime.utcnow().replace(tzinfo=timezone.utc)

    if data["server_is_online"]:
        tags = {
            TagKey.WOW_STATUS: "{} players".format(data["connected_players"]),
            TagKey.WOW_STATUS_MEASURE_TIME: now.isoformat(),
        }
    else:
        tags = {
            TagKey.WOW_STATUS: "stopped",
            TagKey.WOW_STATUS_MEASURE_TIME: now.isoformat(),
        }

    aws_region = Ec2Instance.get_placement_region()
    bsm = BotoSesManager(region_name=aws_region)
    instance_id = Ec2Instance.get_instance_id()
    bsm.ec2_client.create_tags(
        Resources=[instance_id],
        Tags=[dict(Key=k, Value=v) for k, v in tags.items()],
    )
