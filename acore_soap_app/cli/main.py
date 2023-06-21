# -*- coding: utf-8 -*-

"""
SOAP Agent command line user interface.
"""

import typing as T
import fire

from .impl import (
    gm,
)


class Command:
    """
    Acore Soap Agent command line interface.

    Example:

    - acsoap
    """
    # --------------------------------------------------------------------------
    # These two command can only be used on EC2
    # --------------------------------------------------------------------------
    def gm(
        self,
        cmd: str,
        user: T.Optional[str] = None,
        pwd: T.Optional[str] = None,
        raises: bool = True,
        s3uri: T.Optional[str] = None,
    ):
        """
        Run single GM command.

        :param cmd: the GM command to run
        :param user: in game GM account username, if not given, then use "admin"
        :param pwd: in game GM account password, if not given, then use "admin"
        :param raises: raise error if any of the GM command failed.
        :param s3uri: if None, then return the response as JSON, otherwise, save
            the response to S3.

        Example::

            acsoap gm --help

            acsoap gm ".server info"

            acsoap gm ".server info" --user myuser --pwd mypwd

            acsoap gm ".server info" --s3uri s3://bucket/output.json
        """
        gm(
            request_like=cmd,
            username=user,
            password=pwd,
            raises=raises,
            s3uri_output=s3uri,
        )


def run():
    fire.Fire(Command)
