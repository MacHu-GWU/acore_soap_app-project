# -*- coding: utf-8 -*-

from acore_soap_app import api


def test():
    _ = api
    _ = api.DEFAULT_USERNAME
    _ = api.DEFAULT_PASSWORD
    _ = api.DEFAULT_HOST
    _ = api.DEFAULT_PORT
    _ = api.SOAPRequest
    _ = api.SOAPResponse
    _ = api.run_soap_command
    _ = api.canned
    _ = api.canned.extract_online_players
    _ = api.canned.get_online_players
    _ = api.canned.is_server_online
    _ = api.canned.create_account
    _ = api.canned.set_gm_level
    _ = api.canned.set_password
    _ = api.canned.delete_account
    _ = api.canned.gm_list
    _ = api.EC2IsNotRunningError
    _ = api.RunCommandError
    _ = api.SOAPResponseParseError
    _ = api.SOAPCommandFailedError


if __name__ == "__main__":
    from acore_soap_app.tests import run_cov_test

    run_cov_test(__file__, "acore_soap_app.api", preview=False)
