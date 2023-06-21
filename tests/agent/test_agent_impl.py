# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from acore_soap_app.agent.impl import SOAPRequest, SOAPResponse, SoapResponseParseError


dir_here = Path(__file__).absolute().parent

path_fail1_wrong_command_xml = dir_here / "fail1_wrong_command.xml"
path_fail2_account_not_exists_xml = dir_here / "fail2_account_not_exists.xml"
path_success_xml = dir_here / "success.xml"


class TestSOAPRequest:
    def test(self):
        req = SOAPRequest(command=".server info")
        req1 = SOAPRequest.from_json(req.to_json())
        assert req1.to_dict() == req.to_dict()

        assert req.endpoint == "http://admin:admin@localhost:7878/"


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

        with pytest.raises(SoapResponseParseError):
            SOAPResponse.parse("<a>hello</a>")


if __name__ == "__main__":
    from acore_soap_app.tests import run_cov_test

    run_cov_test(__file__, "acore_soap_app.agent.impl", preview=False)
