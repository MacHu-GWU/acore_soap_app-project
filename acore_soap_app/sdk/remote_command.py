# -*- coding: utf-8 -*-

import typing as T
import time

from boto_session_manager import BotoSesManager
import aws_ssm_run_command.api as aws_ssm_run_command
from acore_server_metadata.api import Server

from ..agent.api import SoapResponse
from ..exc import EC2IsNotRunningError, RunCommandError


def build_cli_arg(command: str) -> str:
    return (
        f'/home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap gm "{command}"'
    )


def run_soap_command(
    bsm: BotoSesManager,
    server_id: str,
    command: T.Union[str, T.List[str]],
    sync: bool = True,
    delays: int = 1,
    timeout: int = 10,
    verbose: bool = True,
) -> T.Union[SoapResponse, str,]:
    """
    :param bsm:
    :param server_id:
    :param command: single or list of command you want to execute
    :param sync: if sync mode, then return a :class:`acore_soap_app.agent.impl.SoapResponse`
        object, if async mode, then return a command id.
    :param delays:
    :param timeout:
    :param verbose:
    """
    # preprocess arguments
    if isinstance(command, str):
        commands = [command]
    else:
        commands = command

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
        commands=[build_cli_arg(command) for command in commands],
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
    soap_response = SoapResponse.from_json(output)
    return soap_response
