# -*- coding: utf-8 -*-

import typing as T


if T.TYPE_CHECKING:
    import aws_ssm_run_command.api as aws_ssm_run_command


class EC2IsNotRunningError(SystemError):
    """
    raises when try to run a remote command on a non-running EC2 instance.
    """

    pass


class RunCommandError(SystemError):
    """
    raises when ssm_client.send_command() fails.
    """

    @classmethod
    def from_command_invocation(
        cls,
        command_invocation: "aws_ssm_run_command.better_boto.CommandInvocation",
    ):
        msg = (
            f"return code: {command_invocation.ResponseCode}, "
            f"output: {command_invocation.StandardOutputContent!r}, "
            f"error: {command_invocation.StandardErrorContent!r}, "
        )
        return cls(msg)


class SOAPResponseParseError(ValueError):
    """
    raises when failed to parse the soap response.
    """


class SOAPCommandFailedError(ValueError):
    """
    raises when SOAP command failed
    """
