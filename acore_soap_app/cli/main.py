# -*- coding: utf-8 -*-

import fire

from ..agent.api import run_soap_command


class Command:
    def gm(self, cmd: str):
        res = run_soap_command(command=cmd)
        print(res.to_json())


def run():
    fire.Fire(Command)
