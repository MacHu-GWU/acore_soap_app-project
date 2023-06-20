# -*- coding: utf-8 -*-

from pathlib import Path
from acore_soap_app.agent.impl import SoapResponse


dir_here = Path(__file__).absolute().parent

path_fail1_wrong_command_xml = dir_here / "fail1_wrong_command.xml"
path_fail2_account_not_exists_xml = dir_here / "fail2_account_not_exists.xml"
path_success_xml = dir_here / "success.xml"


class TestSoapResponse:
    def test_parse(self):
        res = SoapResponse.parse(path_fail1_wrong_command_xml.read_text())
        assert res.succeeded is False
        assert "Possible subcommands" in res.message

        res = SoapResponse.parse(path_fail2_account_not_exists_xml.read_text())
        assert res.succeeded is False
        assert "Account not exist: TEST" in res.message

        res = SoapResponse.parse(path_success_xml.read_text())
        assert res.succeeded is True
        assert "Account created: test" in res.message


if __name__ == "__main__":
    from acore_soap_app.tests import run_cov_test

    run_cov_test(__file__, "acore_soap_app.agent.impl", preview=False)
