# -*- coding: utf-8 -*-

"""
todo: add docstring
"""

import typing as T
import xml.etree.ElementTree as ET

import requests
from ..paths import dir_python_lib

path_xml = dir_python_lib.joinpath("agent", "execute-command.xml")
execute_command_xml = path_xml.read_text(encoding="utf-8")


def run_soap_command(
    command: str,
    username: str = "admin",
    password: str = "admin",
) -> T.Optional[str]:
    """
    Run soap command via HTTP request. This function has to be run on the game server
    and talk to the localhost.

    :param command: the command to execute
    :param username: the in game GM account username
    :param username: the in game GM account password

    :return: the result part of the string in xml response. if None,
      means it is failed
    """
    # construct url
    url = f"http://{username}:{password}@localhost:7878/"
    # HTTP headers
    headers = {"Content-Type": "application/xml"}
    # build the final XML request
    xml = path_xml.read_text(encoding="utf-8").format(command=command)
    # send the request
    res = requests.post(url, headers=headers, data=xml)
    print(res.text)
    # parse response
    root = ET.fromstring(res.text)
    results = list(root.iter("result"))
    if len(results):
        return results[0].text
    else:
        return None
