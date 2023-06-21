# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from pathlib import Path

import moto
import pytest

from acore_soap_app.agent.impl import (
    Base,
    SOAPRequest,
    SOAPResponse,
    SOAPResponseParseError,
    get_object,
)
from acore_soap_app.tests.mock_aws import BaseMockTest

dir_here = Path(__file__).absolute().parent

path_fail1_wrong_command_xml = dir_here / "fail1_wrong_command.xml"
path_fail2_account_not_exists_xml = dir_here / "fail2_account_not_exists.xml"
path_success_xml = dir_here / "success.xml"


@dataclasses.dataclass
class User(Base):
    name: T.Optional[str] = dataclasses.field(default=None)
    age: T.Optional[int] = dataclasses.field(default=None)


class TestBase:
    def test(self):
        user = User()
        assert user.to_dict() == {}

        user = User(name="alice", age=25)
        user1 = User.from_json(user.to_json())
        assert user == user1


class TestSOAPRequest(BaseMockTest):
    mock_list = [
        moto.mock_s3,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm.s3_client.create_bucket(Bucket="mybucket")

    def _test_endpoint(self):
        req = SOAPRequest(command=".server info")
        assert req.endpoint == "http://admin:admin@localhost:7878/"

        req.set_default("test", "test")
        assert req.endpoint == "http://test:test@localhost:7878/"

        req.set_default("test1", "test1")
        assert req.endpoint == "http://test:test@localhost:7878/"

    def _test_batch_load_dump(self):
        requests = [
            SOAPRequest(command="command1"),
            SOAPRequest(command="command2"),
        ]
        SOAPRequest.batch_dump_to_s3(
            s3_client=self.bsm.s3_client,
            instances=requests,
            s3uri="s3://mybucket/requests.json",
        )

        json_str = get_object(self.bsm.s3_client, s3uri="s3://mybucket/requests.json")
        assert "username" not in json_str

        requests1 = SOAPRequest.batch_load_from_s3(
            s3_client=self.bsm.s3_client,
            s3uri="s3://mybucket/requests.json",
        )
        assert requests1 == requests

    def _test_batch_load(self):
        SOAPRequest.batch_load("command")
        SOAPRequest.batch_load(["command1", "command2"])
        SOAPRequest.batch_load(
            "s3://mybucket/requests.json",
            s3_client=self.bsm.s3_client,
        )
        SOAPRequest.batch_load(SOAPRequest("command"))
        SOAPRequest.batch_load([SOAPRequest("command1"), SOAPRequest("command2")])

    def test(self):
        self._test_endpoint()
        self._test_batch_load_dump()
        self._test_batch_load()


class TestSoapResponse:
    def test(self):
        res = SOAPResponse.parse(path_fail1_wrong_command_xml.read_text())
        assert res.succeeded is False
        assert "Possible subcommands" in res.message

        res = SOAPResponse.parse(path_fail2_account_not_exists_xml.read_text())
        assert res.succeeded is False
        assert "Account not exist: TEST" in res.message

        res = SOAPResponse.parse(path_success_xml.read_text())
        assert res.succeeded is True
        assert "Account created: test" in res.message

        with pytest.raises(SOAPResponseParseError):
            SOAPResponse.parse("<a>hello</a>")


if __name__ == "__main__":
    from acore_soap_app.tests import run_cov_test

    run_cov_test(__file__, "acore_soap_app.agent.impl", preview=False)
