# -*- coding: utf-8 -*-

"""
这个脚本用于测试在 EC2 实例上运行 Soap 命令. (只能在 EC2 上运行, 不能在本地电脑上运行)
"""

from acore_soap_app.agent.api import SOAPRequest

command = "server info"
# command = ".account onlinelist"

response = SOAPRequest(command=command).send()
response.print()
