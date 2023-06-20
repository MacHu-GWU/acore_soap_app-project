# -*- coding: utf-8 -*-

import typing as T
import json
import fire
from boto_session_manager import BotoSesManager

from ..agent.api import run_soap_command as run_local_soap_command, get_boto_ses
from ..sdk.api import run_soap_command as run_remote_soap_command


def ensure_ec2_environment():
    if not __file__.startswith("/home/ubuntu"):
        raise EnvironmentError("This is not a EC2 environment")


class Command:
    # --------------------------------------------------------------------------
    #
    # --------------------------------------------------------------------------
    def gm(
        self,
        cmd: str,
        username: str = "admin",
        password: str = "admin",
    ):
        """
        Example: acsoap gm ".server info"
        """
        ensure_ec2_environment()
        soap_res = run_local_soap_command(
            command=cmd, username=username, password=password
        )
        print(soap_res.to_json())

    def s3_gm(
        self,
        s3uri_input: str,
        s3uri_output: str,
    ):
        ensure_ec2_environment()
        boto_ses = get_boto_ses()
        s3_client = boto_ses.client("s3")
        parts = s3uri_input.split("/", 3)
        bucket, key = parts[2], parts[3]
        get_object_response = s3_client.get_object(Bucket=bucket, Key=key)
        records: T.List[T.Dict[str, str]] = json.loads(
            get_object_response["Body"].read().decode("utf-8")
        )
        results: T.List[T.Dict[str, str]] = [
            run_local_soap_command(**record).to_dict() for record in records
        ]
        parts = s3uri_output.split("/", 3)
        bucket, key = parts[2], parts[3]
        s3_client.put_object(Bucket=bucket, Key=key, Body=json.dumps(results))
        print(f"results saved to {s3uri_output}")

    def remote_gm(
        self,
        server_id: str,
        cmd: str,
        username: str = "admin",
        password: str = "admin",
        region: T.Optional[str] = None,
        profile: T.Optional[str] = None,
        delays: int = 1,
        timeout: int = 10,
        verbose: bool = True,
    ):
        """
        Example: acsoap gm ".server info"
        """
        bsm = BotoSesManager(region_name=region, profile_name=profile)
        soap_res = run_remote_soap_command(
            bsm=bsm,
            server_id=server_id,
            cmd=cmd,
            username=username,
            password=password,
            sync=True,
            delays=delays,
            timeout=timeout,
            verbose=verbose,
        )
        print(soap_res.to_json())


def run():
    fire.Fire(Command)
