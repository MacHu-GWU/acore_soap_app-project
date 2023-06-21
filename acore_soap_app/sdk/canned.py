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

from ..agent.api import SOAPResponse
from ..exc import SOAPResponseParseError, SOAPCommandFailedError
from .core import run_soap_command


def get_online_players(
    bsm: BotoSesManager,
    server_id: str,
    raises: bool = True,
) -> T.Dict[str, int]:
    response = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        request_like=".server info",
        raises=raises,
    )[0]

    res = re.findall("Connected players: (\d+)", response.message)
    if len(res) == 1:
        connected_players = int(res[0])
    else:
        raise SOAPResponseParseError(response.message)

    res = re.findall("Characters in world: (\d+)", response.message)
    if len(res) == 1:
        characters_in_world = int(res[0])
    else:
        raise SOAPResponseParseError(response.message)

    return {
        "connected_players": connected_players,
        "characters_in_world": characters_in_world,
    }


def is_server_online(
    bsm: BotoSesManager,
    server_id: str,
    raises: bool = True,
) -> bool:
    result = get_online_players(bsm, server_id, raises=raises)
    return True


def create_account(
    bsm: BotoSesManager,
    server_id: str,
    username: str,
    password: str,
    raises: bool = True,
) -> bool:
    """
    :return: a boolean value to indicate whether the account is created successfully
    """
    response = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        request_like=f".account create {username} {password}",
        raises=raises,
    )[0]
    response.print()
    return response.succeeded


def set_gm_level(
    bsm: BotoSesManager,
    server_id: str,
    username: str,
    level: int,
    realm_id: int,
    raises: bool = True,
) -> bool:
    """

    :param username:
    :param level:
    :param realm_id:
    :return: a boolean value to indicate whether the account is created successfully
    """
    response = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        request_like=f".account set gmlevel {username} {level} {realm_id}",
        raises=raises,
    )[0]
    response.print()
    return response.succeeded


def set_password(
    bsm: BotoSesManager,
    server_id: str,
    username: str,
    password: str,
    raises: bool = True,
) -> bool:
    """

    :param username:
    :param level:
    :param realm_id:
    :return: a boolean value to indicate whether the account is created successfully
    """
    response = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        request_like=f".account set password {username} {password} {password}",
        raises=raises,
    )[0]
    response.print()
    return response.succeeded


def delete_account(
    bsm: BotoSesManager,
    server_id: str,
    username: str,
    raises: bool = True,
) -> bool:
    """
    :return: a boolean value to indicate whether the account is deleted successfully
    """
    response = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        request_like=f".account delete {username}",
        raises=raises,
    )[0]
    response.print()
    return response.succeeded


def gm_list(
    bsm: BotoSesManager,
    server_id: str,
    raises: bool = True,
) -> T.List[T.Tuple[str, int]]:
    """
    :return: a boolean value to indicate whether the account is deleted successfully
    """
    response = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        request_like=f".gm list",
        raises=raises,
    )[0]
    print(response.message)
    if response.succeeded:
        results = list()
        lines = response.message.splitlines()
        for line in lines:
            if line.startswith("|"):
                words = [word.strip() for word in line.split("|") if word.strip()]
                results.append((words[0], int(words[1])))
        return results
    else:
        raise SOAPCommandFailedError
