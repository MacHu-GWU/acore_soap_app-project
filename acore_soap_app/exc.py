# -*- coding: utf-8 -*-

import typing as T


if T.TYPE_CHECKING:
    import aws_ssm_run_command.api as aws_ssm_run_command


class EC2IsNotRunningError(SystemError):
    pass


class SoapResponseParseError(ValueError):
    pass


class RunCommandError(SystemError):
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
