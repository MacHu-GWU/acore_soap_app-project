# -*- coding: utf-8 -*-

import typing as T
import json
import fire
import boto3

from ..agent.api import run_soap_command, get_boto_ses


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
        res = run_soap_command(command=cmd, username=username, password=password
        print(res.to_json())

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
            run_soap_command(**record).to_dict()
            for record in records
        ]
        parts = s3uri_output.split("/", 3)
        bucket, key = parts[2], parts[3]
        s3_client.put_object(Bucket=bucket, Key=key, Body=json.dumps(results))
        print(f"results saved to {s3uri_output}")


def run():
    fire.Fire(Command)
