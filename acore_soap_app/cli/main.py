# -*- coding: utf-8 -*-

import fire
from ..agent.api import run_soap_command




class Command:
    def gm(self, cmd: str):
        response = run_soap_command(command=cmd)
        if response is None:
            print("No response")
        else:
            print(response)


def run():
    fire.Fire(Command)
