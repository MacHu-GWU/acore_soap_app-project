# -*- coding: utf-8 -*-

import typing as T
import json
import fire
from boto_session_manager import BotoSesManager

from .impl import (
    gm,
    batch_gm,
)
from ..agent.api import (
    SOAPRequest,
    SOAPResponse,
    get_boto_ses,
)


def ensure_ec2_environment():
    if not __file__.startswith("/home/ubuntu"):
        raise EnvironmentError("This is not a EC2 environment")


class Command:
    # --------------------------------------------------------------------------
    # These two command can only be used on EC2
    # --------------------------------------------------------------------------
    def gm(
        self,
        cmd: str,
        user: T.Optional[str] = None,
        pwd: T.Optional[str] = None,
        s3uri: T.Optional[str] = None,
    ):
        """
        Run single GM command.

        :param cmd: the GM command to run
        :param user: in game GM account username, if not given, then use "admin"
        :param pwd: in game GM account password, if not given, then use "admin"
        :param s3uri: if None, then return the response as JSON, otherwise, save
            the response to S3.

        Example:

        - ``acsoap gm --help``
        - ``acsoap gm ".server info"``
        - ``acsoap gm s3://bucket/request.json``
        """
        if cmd.startswith("s3://"):
            request = cmd
        else:
            request = SOAPRequest(command=cmd, username=user, password=pwd)
        gm(request=request, username=user, password=pwd, s3uri_output=s3uri)

    def batch_gm(
        self,
        s3uri_in: str,
        user: T.Optional[str] = None,
        pwd: T.Optional[str] = None,
        raises: bool = True,
        s3uri_out: T.Optional[str] = None,
    ):
        """
        Run sequence of GM commands.

        :param s3uri_in: the S3 URI of the JSON file that contains the soap requests,
            example: ``[{"command": ".account create test1 ..."}, {"command": ".account create test2 ..."}]``
        :param user: in game GM account username, if not given, then use "admin"
        :param pwd: in game GM account password, if not given, then use "admin"
        :param raises: raise error if any of the GM command failed.
        :param s3uri_out: if None, then return the response as JSON, otherwise, save
            the response to S3.
        """
        batch_gm(
            requests=s3uri_in,
            username=user,
            password=pwd,
            stop_on_error=raises,
            s3uri_output=s3uri_out,
        )

    # def remote_gm(
    #     self,
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


def run():
    fire.Fire(Command)
