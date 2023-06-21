# -*- coding: utf-8 -*-

"""
这个模块用来测试运行封装好的命令.
"""

from boto_session_manager import BotoSesManager
from acore_soap_app.sdk.api import canned

bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
server_id = "sbx-blue"

print(canned.get_online_players(bsm, server_id))
print(canned.is_server_online(bsm, server_id))

print(canned.create_account(bsm, server_id, "test1", "1234"))
print(canned.set_gm_level(bsm, server_id, "test1", 3, -1))
print(canned.set_password(bsm, server_id, "test1", "123456"))
print(canned.delete_account(bsm, server_id, "test1"))

print(canned.gm_list(bsm, server_id))
