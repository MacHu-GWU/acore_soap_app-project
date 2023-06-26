# -*- coding: utf-8 -*-

"""
对具体的 GM 命令业务逻辑高度封装后的接口. 这些接口可以分为两类:

1. 我们只关心运行成功与否, 不关心返回值.
2. 我们需要这个命令返回的数据.

所有的接口都有这三个参数:

- bsm: ``boto_session_manager.BotoSesManager`` 对象, 定义了 AWS 权限.
- server_id: 服务器的逻辑 ID, 命名规则为 ``${env_name}-${server_name}``. 例如 ``sbx-blue``.
- raises: 当命令执行失败时是否抛出异常, 默认为 ``True``.

Reference:

- https://www.azerothcore.org/wiki/gm-commands
"""

import typing as T
import re
from boto_session_manager import BotoSesManager

from ...exc import SOAPResponseParseError, SOAPCommandFailedError
from ..core import run_soap_command


def extract_online_players(message: str) -> T.Tuple[int, int]:
    res = re.findall(r"Connected players: (\d+)", message)
    if len(res) == 1:
        connected_players = int(res[0])
    else:  # pragma: no cover
        raise SOAPResponseParseError(message)

    res = re.findall(r"Characters in world: (\d+)", message)
    if len(res) == 1:
        characters_in_world = int(res[0])
    else:  # pragma: no cover
        raise SOAPResponseParseError(message)

    return connected_players, characters_in_world


def get_online_players(
    bsm: BotoSesManager,
    server_id: str,
    raises: bool = True,
) -> T.Dict[str, int]:
    """
    :return: a dict with two keys: ``connected_players`` and ``characters_in_world``.
    """
    response = run_soap_command(
        bsm=bsm,
        server_id=server_id,
        request_like=".server info",
        raises=raises,
    )[0]

    connected_players, characters_in_world = extract_online_players(response.message)

    return {
        "connected_players": connected_players,
        "characters_in_world": characters_in_world,
    }


def is_server_online(
    bsm: BotoSesManager,
    server_id: str,
    raises: bool = True,
) -> bool:
    """
    :return: a boolean value to indicate whether the server is online
    """
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
    :param username:

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
