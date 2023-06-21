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


def build_cli_arg_for_gm(
    command: str,
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
    raises: bool = True,
    s3uri_output: T.Optional[str] = None,
    path_cli: str = "/home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap",
) -> str:
    """
    构造最终的命令行参数.
    """
    args = [
        path_cli,
        "gm",
        f'"{command}"',
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
    if s3uri_output is not None:
        args.append(f"-s={s3uri_output}")
    return " ".join(args)


def run_soap_command(
    bsm: BotoSesManager,
    server_id: str,
    request_like: T.Union[
        str,
        T.List[str],
        SOAPRequest,
        T.List[SOAPRequest],
    ],
    username: T.Optional[str] = None,
    password: T.Optional[str] = None,
    raises: bool = True,
    s3uri_input: T.Optional[str] = None,
    s3uri_output: T.Optional[str] = None,
    path_cli: str = "/home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap",
    sync: bool = True,
    delays: int = 1,
    timeout: int = 10,
    verbose: bool = True,
) -> T.Union[T.List[SOAPResponse], str]:
    """
    从任何地方, 通过 SSM Run Command, 远程执行 SOAP 命令.

    Usage Example:

    .. code-block:: python

        >>> response = run_soap_command(bsm, "sbx-blue", ".server info")
        >>> response = run_soap_command(bsm, "sbx-blue", [".account create test1 test1", ".account create test2 test2"])

    :param bsm: ``boto_session_manager.BotoSesManager`` 对象, 定义了 AWS 权限.
    :param server_id: AzerothCore 服务器的逻辑 ID, 命名规律为 "${env_name}-${server_name}",
        例如 "sbx-blue"
    :param request_like: 请参考
        :class:`~acore_soap_app.agent.impl.SOAPRequest.batch_load`
    :param username: 默认的用户名, 只有当 request.username 为 None 的时候才会用到.
    :param password: 默认的密码, 只有当 request.password 为 None 的时候才会用到.
    :param raises: 默认为 True. 如果为 True, 则在遇到错误时抛出异常. 反之则将
        failed SOAP Response 原封不动地返回.
    :param s3uri_input: 如果指定, 则将输入写入 S3. 常用于 Payload 比较大的情况.
        如果你一次性发送的 request 大于 20 条, 则必须使用这个参数.
    :param s3uri_output: 如果不指定, 则默认将输出作为 JSON 打印. 如果指定了 s3uri,
        则将输出写入到 S3.
    :param path_cli: EC2 上 acsoap 命令行工具的绝对路径.
    :param sync: 同步和异步模式, 默认为同步模式
        - 如果以同步模式运行, 则会等待 SSM Run Command 完成
        - 如果以异步模式运行, 则会立刻返回一个 SSM Run Command 的 command id.
    :param delays: 同步模式下的等待间隔
    :param timeout: 同步模式下的超时限制
    :param verbose: 同步模式下是否显示进度条
    """
    # load requests
    requests = SOAPRequest.batch_load(
        request_like=request_like,
        username=username,
        password=password,
        s3_client=bsm.s3_client,
    )

    # get ec2 instance id
    server = Server(id=server_id)
    server.refresh(ec2_client=bsm.ec2_client, rds_client=bsm.rds_client)
    if server.is_running() is False:
        raise EC2IsNotRunningError(f"EC2 {server_id!r} is not running")
    instance_id = server.ec2_inst.id

    # identify the run strategy
    if len(requests) >= 20:
        if s3uri_input is None:
            raise ValueError(
                "'s3uri_input' must be specified when the number of requests is greater than 20"
            )
        is_s3_input = True
    else:
        is_s3_input = s3uri_input is not None

    if is_s3_input:
        SOAPRequest.batch_dump_to_s3(
            s3_client=bsm.s3_client,
            instances=requests,
            s3uri=s3uri_input,
        )
        commands = [
            build_cli_arg_for_gm(
                command=s3uri_input,
                username=username,
                password=password,
                raises=raises,
                s3uri_output=s3uri_output,
                path_cli=path_cli,
            )
        ]
    else:
        commands = [
            build_cli_arg_for_gm(
                command=request.command,
                username=request.username,
                password=request.password,
                raises=raises,
                s3uri_output=s3uri_output,
                path_cli=path_cli,
            )
            for request in requests
        ]

    # run command
    command_id = aws_ssm_run_command.better_boto.send_command(
        ssm_client=bsm.ssm_client,
        instance_id=instance_id,
        commands=commands,
    )
    if sync is False:  # async mode, return immediately
        return command_id

    # sync mode, wait until command succeeded
    time.sleep(1)

    # get command response
    command_invocation = aws_ssm_run_command.better_boto.wait_until_command_succeeded(
        ssm_client=bsm.ssm_client,
        command_id=command_id,
        instance_id=instance_id,
        raises=False,
        delays=delays,
        timeout=timeout,
        verbose=verbose,
    )
    if command_invocation.ResponseCode != 0:
        raise RunCommandError.from_command_invocation(command_invocation)

    # parse response
    if s3uri_output is None:
        output = command_invocation.StandardOutputContent
        lines = output.splitlines()
        responses = [SOAPResponse.from_json(json_str) for json_str in lines]
    else:
        responses = SOAPResponse.batch_load_from_s3(
            s3_client=bsm.s3_client, s3uri=s3uri_output
        )
    return responses
