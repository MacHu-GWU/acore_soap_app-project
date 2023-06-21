Agent and SDK
==============================================================================


Overview
------------------------------------------------------------------------------
该项目本身是一个可安装的 Python 库. 里面包含两个重要模块 Agent 和 SDK.

Agent 是一个需要再 EC2 游戏服务器上安装的 CLI 程序. 它对 SOAP 的 HTTP Request 和 XML input / output 进行了封装, 提供了一套 CLI 接口用于在服务器上执行 GM 命令. 它是所有需要远程执行 GM 命令的外部程序的代理. 有了它, 我们就可以通过 `AWS SSM Run Command <https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command.html>`_ 这个服务安全地在 EC2 执行任何远程命令. 强调一下, Agent 必须要在 EC2 游戏服务器上安装.

SDK 则是一套开发者工具. 它对用 Run Command Service 远程执行 CLI 的业务逻辑进行了封装, 并且做出了很多优化, 例如利用 AWS S3 储存输入和输出结果, 以应对批量执行大量命令的情况, 还例如非常高级的异常处理. 基于这套 SDK, 开发者可以很容易地开发出远程执行 GM 命令的应用程序, 将其嵌入到魔兽世界服务器管理后台中.


Agent
------------------------------------------------------------------------------
:class:`~acore_soap_app.cli.main.Command` 定义了 SOAP Agent CLI 的命令和参数.


SDK
------------------------------------------------------------------------------
下面这个例子展示了如何用 :func:`~acore_soap_app.sdk.core.run_soap_command` 函数来在任何地方远程执行 GM 命令.

.. literalinclude:: ../../../examples/run_soap_command.py
   :language: python
   :linenos:

:mod:`~acore_soap_app.sdk.core.canned` 模块 还提供了许多对具体的 GM 命令业务逻辑高度封装后的接口. 更加的 Pythonic.

.. literalinclude:: ../../../examples/run_canned_command.py
   :language: python
   :linenos:

