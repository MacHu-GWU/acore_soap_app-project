# -*- coding: utf-8 -*-

from acore_soap_app.agent.soap_agent import run_soap_command

# command = "server info"
command = ".account onlinelist"
response = run_soap_command(command=command)
print(response)