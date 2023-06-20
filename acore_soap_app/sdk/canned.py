# -*- coding: utf-8 -*-

"""
- 我们只关心运行成功与否, 不关心返回值.
- 我们需要这个命令返回的数据.

Reference:

- https://www.azerothcore.org/wiki/gm-commands
"""

import typing as T
import re
from boto_session_manager import BotoSesManager
import aws_ssm_run_command.api as aws_ssm_run_command

from ..agent.api import SoapResponse
from ..exc import SoapResponseParseError, SoapCommandFailedError
from .remote_command import run_soap_command


def get_online_players(
    bsm: BotoSesManager,
    server_id: str,
) -> T.Dict[str, int]:
    soap_res = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        cmd=".server info",
    )

    res = re.findall("Connected players: (\d+)", soap_res.message)
    if len(res) == 1:
        connected_players = int(res[0])
    else:
        raise SoapResponseParseError(soap_res.message)

    res = re.findall("Characters in world: (\d+)", soap_res.message)
    if len(res) == 1:
        characters_in_world = int(res[0])
    else:
        raise SoapResponseParseError(soap_res.message)

    return {
        "connected_players": connected_players,
        "characters_in_world": characters_in_world,
    }


def is_server_online(
    bsm: BotoSesManager,
    server_id: str,
) -> bool:
    result = get_online_players(bsm, server_id)
    return True


def create_account(
    bsm: BotoSesManager,
    server_id: str,
    username: str,
    password: str,
) -> bool:
    """
    :return: a boolean value to indicate whether the account is created successfully
    """
    soap_res = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        cmd=f".account create {username} {password}",
    )
    soap_res.print()
    return soap_res.succeeded


def set_gm_level(
    bsm: BotoSesManager,
    server_id: str,
    username: str,
    level: int,
    realm_id: int,
) -> bool:
    """

    :param username:
    :param level:
    :param realm_id:
    :return: a boolean value to indicate whether the account is created successfully
    """
    soap_res = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        cmd=f".account set gmlevel {username} {level} {realm_id}",
    )
    soap_res.print()
    return soap_res.succeeded


def set_password(
    bsm: BotoSesManager,
    server_id: str,
    username: str,
    password: str,
) -> bool:
    """

    :param username:
    :param level:
    :param realm_id:
    :return: a boolean value to indicate whether the account is created successfully
    """
    soap_res = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        cmd=f".account set password {username} {password} {password}",
    )
    soap_res.print()
    return soap_res.succeeded


def delete_account(
    bsm: BotoSesManager,
    server_id: str,
    username: str,
) -> bool:
    """
    :return: a boolean value to indicate whether the account is deleted successfully
    """
    soap_res = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        cmd=f".account delete {username}",
    )
    soap_res.print()
    return soap_res.succeeded


def gm_list(
    bsm: BotoSesManager,
    server_id: str,
) -> T.List[T.Tuple[str, int]]:
    """
    :return: a boolean value to indicate whether the account is deleted successfully
    """
    soap_res = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        cmd=f".gm list",
    )
    print(soap_res.message)
    if soap_res.succeeded:
        results = list()
        lines = soap_res.message.splitlines()
        for line in lines:
            if line.startswith("|"):
                words = [word.strip() for word in line.split("|") if word.strip()]
                results.append((words[0], int(words[1])))
        return results
    else:
        raise SoapCommandFailedError
