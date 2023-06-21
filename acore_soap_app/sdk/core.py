# -*- coding: utf-8 -*-

"""
这是 SDK 的核心模块, 实现了各种底层方法.
"""

import typing as T
import time

from boto_session_manager import BotoSesManager
import aws_ssm_run_command.api as aws_ssm_run_command
from acore_server_metadata.api import Server

from ..agent.api import SOAPRequest, SOAPResponse
from ..exc import EC2IsNotRunningError, RunCommandError
from ..utils import get_object, put_object


def build_cli_arg_for_gm(
    cmd: str,
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
    raises: T.Optional[bool] = True,
    s3uri: T.Optional[str] = None,
    path_cli: str = "/home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap",
) -> str:
    args = [
        path_cli,
        "gm",
        f'"{cmd}"',
    ]
    if username is not None:
        args.append(f"-u={username}")
    if password is not None:
        args.append(f"-p={password}")
    if raises is not None:
        if raises:
            args.append(f"-r=True")
        else:
            args.append(f"-r=False")
    if s3uri is not None:
        args.append(f"-s={s3uri}")
    return " ".join(args)


def build_cli_arg_for_batch_gm(
    s3uri_in: str,
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
    raises: T.Optional[bool] = True,
    s3uri_out: T.Optional[str] = None,
    path_cli: str = "/home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap",
) -> str:
    args = [
        path_cli,
        "batch-gm",
        f'"{s3uri_in}"',
    ]
    if username is not None:
        args.append(f"-u={username}")
    if password is not None:
        args.append(f"-p={password}")
    if raises is not None:
        if raises:
            args.append(f"-r=True")
        else:
            args.append(f"-r=False")
    if s3uri_out is not None:
        args.append(f"-s={s3uri_out}")
    return " ".join(args)


def run_soap_command(
    bsm: BotoSesManager,
    server_id: str,
    request: T.Union[
        str,
        T.List[str],
        SOAPRequest,
        T.List[SOAPRequest],
    ],
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
    raises: T.Optional[bool] = True,
    s3uri_out: T.Optional[str] = None,
    sync: bool = True,
    delays: int = 1,
    timeout: int = 10,
    verbose: bool = True,
) -> T.Union[SOAPResponse, str]:
    """
    从任何地方, 通过 SSM Run Command, 远程执行 SOAP 命令.

    :param bsm:
    :param server_id:
    :param request: 代表着要运行的 GM 命令, 它可能是以下几种形式中的一种.
        - 如果是一个字符串:
            - 如果是以 s3:// 开头, 那么就去 S3 读数据:
                - 如果读到的数据是单个字典, 那么就视为一个 SOAPRequest.
                - 如果读到的数据是一个列表, 那么就视为多个 SOAPRequest.
            - 如果不是以 s3:// 开头, 那么就视为一个 GM command.
        - 如果是一个字符串列表, 那么就视为多个 GM 命令.
        - 它还可以是单个 SOAPRequest 或 SOAPRequest 列表.
        - 这个参数最终都会被转换成 SOAPRequest 的列表.
    :param raises: 在运行一系列命令时, 如果出错时是否抛出异常, 还是说将
        failed SOAP XML response 原封不动的返回.
    :param s3uri_out: 如果不指定, 则默认将输出作为 JSON 打印. 如果指定了 s3uri,
        则将输出写入到 S3.
    :param sync: 同步和异步模式
        - 如果以同步模式运行, 则会等待 SSM Run Command 完成
        - 如果以异步模式运行, 则会立刻返回一个 SSM Run Command 的 command id.
    :param delays: 同步模式下的等待间隔
    :param timeout: 同步模式下的超时限制
    :param verbose: 同步模式下是否显示进度条
    """
    # preprocess arguments
    if isinstance(request, str):
        if request.startswith("s3://"):
            data = get_object(s3_client=bsm.s3_client, s3uri=request)
            if isinstance(data, dict):
                requests = [SOAPRequest.from_dict(data)]
            elif isinstance(data, list):
                requests = [SOAPRequest.from_dict(dct) for dct in data]
            else:  # pragma: no cover
                raise TypeError
        else:
            requests = [SOAPRequest(command=request)]
    elif isinstance(request, SOAPRequest):
        requests = [request]
    elif isinstance(request, list):
        if isinstance(request[0], str):
            requests = [SOAPRequest(command=item) for item in request]
        elif isinstance(request[0], SOAPRequest):
            requests = request
        else:
            raise TypeError
    else:  # pragma: no cover
        raise TypeError(f"request must be str or SOAPRequest, not {type(request)}")

    for request_ in requests:
        request_.set_default(username=username, password=password)

    # get ec2 instance id
    server = Server(id=server_id)
    server.refresh(ec2_client=bsm.ec2_client, rds_client=bsm.rds_client)
    if server.is_running() is False:
        raise EC2IsNotRunningError(f"EC2 {server_id!r} is not running")
    instance_id = server.ec2_inst.id

    # run command
    command_id = aws_ssm_run_command.better_boto.send_command(
        ssm_client=bsm.ssm_client,
        instance_id=instance_id,
        commands=[
            build_cli_arg(
                cmd=command,
                username=username,
                password=password,
            )
            for command in commands
        ],
    )
    if sync is False:
        return command_id

    time.sleep(1)

    # get command response
    command_invocation = aws_ssm_run_command.better_boto.wait_until_command_succeeded(
        ssm_client=bsm.ssm_client,
        command_id=command_id,
        instance_id=instance_id,
        delays=delays,
        timeout=timeout,
        verbose=verbose,
    )

    if command_invocation.ResponseCode != 0:
        raise RunCommandError.from_command_invocation(command_invocation)

    # parse response
    output = command_invocation.StandardOutputContent
    soap_response = SOAPResponse.from_json(output)
    return soap_response


# def run_bulk_soap_command(
#     bsm: BotoSesManager,
#     server_id: str,
#     cmd: T.Union[str, T.List[str]],
#     username: T.Optional[str] = None,
#     password: T.Optional[str] = None,
#     sync: bool = True,
#     delays: int = 1,
#     timeout: int = 10,
#     verbose: bool = True,
# ) -> T.Union[SoapResponse, str]:
