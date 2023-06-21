# -*- coding: utf-8 -*-

"""
这个模块用来测试运行封装好的命令.
"""

from boto_session_manager import BotoSesManager
from acore_soap_app.sdk.api import run_soap_command

bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
server_id = "sbx-blue"

commands = [
    ".account delete test1",
    ".account create test1 1234",
    ".account set gmlevel test1 3 -1",
    ".account set password test1 123456 123456",
]

command_id = run_soap_command(
    bsm=bsm,
    server_id=server_id,
    request_like=commands,
    sync=False,
)
