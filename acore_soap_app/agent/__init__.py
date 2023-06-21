# -*- coding: utf-8 -*-

"""
SOAP agent is a command line tool on the EC2 server that can run GM command
via SOAP protocol and return the SOAP XML response in JSON format.

With a SOAP agent installed, developer can use AWS SSM run command feature to
run this CLI command remotely from anywhere (if have the right permission).

[CN]

SOAP Agent 是 一个在 EC2 服务器上的命令行工具 (你需要 pip install 安装), 它可以通过
SOAP 协议来运行 GM 命令, 并获得 JSON 格式的响应. SOAP Agent 是游戏内 GM 运营自动化的核心,
它提供了一个接口, 使得开发者可以在任何有权限的地方, 通过 AWS SSM run command 的功能, 执行
单个或批量 GM 命令. 如果输入和输出都很大, 还可以使用 AWS S3 作为数据储存的媒介.
"""
