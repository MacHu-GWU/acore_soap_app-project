Agent and SDK
==============================================================================


Overview
------------------------------------------------------------------------------
该项目本身是一个可安装的 Python 库. 里面包含两个重要模块 :ref:`agent` 和 :ref:`sdk`.

:ref:`agent` 是一个需要再 EC2 游戏服务器上安装的 CLI 程序. 它对 SOAP 的 HTTP Request 和 XML input / output 进行了封装, 提供了一套 CLI 接口用于在服务器上执行 GM 命令. 它是所有需要远程执行 GM 命令的外部程序的代理. 有了它, 我们就可以通过 `AWS SSM Run Command <https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command.html>`_ 这个服务安全地在 EC2 执行任何远程命令. 强调一下, Agent 必须要在 EC2 游戏服务器上安装.

:ref:`sdk` 则是一套开发者工具. 它对用 Run Command Service 远程执行 CLI 的业务逻辑进行了封装, 并且做出了很多优化, 例如利用 AWS S3 储存输入和输出结果, 以应对批量执行大量命令的情况, 还例如非常高级的异常处理. 基于这套 SDK, 开发者可以很容易地开发出远程执行 GM 命令的应用程序, 将其嵌入到魔兽世界服务器管理后台中.

.. _agent:

Agent
------------------------------------------------------------------------------
.. important::

    Agent 只能在 EC2 上使用. Agent 在本地电脑上是无法运行的, 因为 SOAP server 是运行在 EC2 上的, 且 SOAP server 不对 public network 开放.

    如果我们要远程使用 Agent 的功能, 请参考 :ref:`sdk` 部分.

用户可以在游戏服务器的 EC2 上使用 ``acsoap gm "{gm command}"`` 这样的 CLI 命令来执行 GM 命令. Agent 的 CLI 命令是 ``acsoap``, 这个命令是在 ``setup.py`` 文件中注册的.

.. dropdown:: setup.py

    .. code-block:: python

        setup(
            ...,
            entry_points={
                "console_scripts": [
                    "acsoap=acore_soap_app.cli.main:run",
                ],
            },
        )

Agent 的核心命令是 ``acsoap gm "{gm command}"``, 该命令由 :meth:`acore_soap_app.cli.main.Command.gm` 方法实现. 它不仅能运行 GM 命令, 还能将返回的信息写入到 AWS S3 上以方便读取.

Agent 的底层是两个对象 :class:`~acore_soap_app.agent.impl.SOAPRequest` 和 :class:`~acore_soap_app.agent.impl.SOAPResponse`. 前者负责构造 SOAP 请求并发送到本地的 SOAP 服务器, 后者负责解析 SOAP 响应. 前面的 :meth:`acore_soap_app.cli.main.Command.gm`

在我们这个项目中, 我们的 ``acsoap`` CLI 可执行文件会被放在 ubuntu 服务器上的 ``/home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap`` 这个位置.

下面列出了部分常用 Agent 的 CLI 命令的功能和语法. 至于详细的命令和参数列表, 请参考 :mod:`~acore_soap_app.cli.main` 模块的文档.

查看服务器状态. 在 EC2 上安装了这个库之后, 你可以用这个命令来测试:

.. code-block:: bash

    /home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap gm ".server info"

创建新账号:

.. code-block:: bash

    /home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap gm ".account create myusername mypassword"

查看在线玩家数量:

.. code-block:: bash

    /home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap canned count-online-players


SDK
------------------------------------------------------------------------------
:func:`~acore_soap_app.sdk.core.run_soap_command` 是 SDK 的核心函数, 它可以将 GM 命令从任何地方, 例如 EC2, ECS, Lambda, 或是本地电脑, 发送到游戏服务器上运行, 并获得返回的结果. 其他的 SDK 函数都是对这个函数的封装. 这个函数的底层实现是 build 好 :ref:`agent` CLI 所需要的 CLI 命令, 然后使用 `aws_ssm_run_command <https://github.com/MacHu-GWU/aws_ssm_run_command-project>`_ 这个库远程执行这个 :meth:`acore_soap_app.cli.main.Command.gm` CLI. 根据你的参数, 你可以选 SOAP response 打印到 stdout 或是写入到 S3. 而无论你将 SOAP response 发到哪里, :func:`~acore_soap_app.sdk.core.run_soap_command` 都会自动的去对应的地方获取数据并返回.


Without SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
下面这个例子展示了如何用 :func:`~acore_soap_app.agent.impl.SOAPRequest` 函数来 **在服务器上 (要手动 SSH 进去)** 编写基于 SOAP 的自动化脚本.

.. literalinclude:: ../../../examples/run_soap_command.py
   :language: python
   :linenos:


Basic Usage of SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
下面这个例子展示了如何用 :func:`~acore_soap_app.sdk.core.run_soap_command` 函数来在 **任何地方远程执行** GM 命令.

.. literalinclude:: ../../../examples/run_remote_command.py
   :language: python
   :linenos:


Canned SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:mod:`~acore_soap_app.sdk.core.canned` 模块 还提供了许多对 **具体的 GM 命令业务逻辑高度封装后的接口**. 更加的 Pythonic. 在这个例子中, 我们展示了如果在任何地方获得在线玩家数量, 查看服务器在线状态等. 下面是一个这个脚本的代码:

.. literalinclude:: ../../../examples/run_canned_command.py
   :language: python
   :linenos:

我们这里以获得在线玩家数量为例. 我们调用了 :func:`~acore_soap_app.sdk.canned.impl.get_online_players` 函数. 而这个函数实际上是调用了 :func:`~acore_soap_app.sdk.core.run_soap_command` 函数并远程执行了 ``.server info`` 命令, 然后对 soap response message 进行解析, 提取出在线玩家数量的信息.


What's Next
------------------------------------------------------------------------------
了解了 Agent 和 SDK 两个组件以后, 我们可以进入下一篇文档, 来看看一些小工具吧.
