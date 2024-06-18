
.. image:: https://readthedocs.org/projects/acore-soap-app/badge/?version=latest
    :target: https://acore-soap-app.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/acore_soap_app-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/acore_soap_app-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/acore_soap_app-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/acore_soap_app-project

.. image:: https://img.shields.io/pypi/v/acore-soap-app.svg
    :target: https://pypi.python.org/pypi/acore-soap-app

.. image:: https://img.shields.io/pypi/l/acore-soap-app.svg
    :target: https://pypi.python.org/pypi/acore-soap-app

.. image:: https://img.shields.io/pypi/pyversions/acore-soap-app.svg
    :target: https://pypi.python.org/pypi/acore-soap-app

.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/acore_soap_app-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/acore_soap_app-project

------

.. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://acore-soap-app.readthedocs.io/en/latest/

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://acore-soap-app.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/acore_soap_app-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/acore_soap_app-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/acore_soap_app-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/acore-soap-app#files


Welcome to ``acore_soap_app`` Documentation
==============================================================================
.. image:: https://acore-soap-app.readthedocs.io/en/latest/_static/acore_soap_app-logo.png
    :target: https://acore-soap-app.readthedocs.io/en/latest/

`azerothcore 魔兽世界服务器 <https://www.azerothcore.org/>`_ 自带一个类似于 Terminal 的交互式 Console. GM 可以在里面输入命令来创建账号, 修改密码, 封禁账号等, 例如 ``.account create $account $password``. 你如果用 GM 账号登录游戏客户端, 你也可以在游戏内聊天框输入 GM 命令, 本质是一样的.

如果你希望像操作 Rest API 一样的远程执行命令, 以上两种方法就不太实用了. 一种你需要 SSH 到服务器上才能接触到 console, 一种你需要登录游戏客户端, 而客户端是没有我们需要的变成接口的. 而这种需求对于服务器维护者来说又是实实在在的. 例如服务器可能有一个官网, 让会员用户可以在网站上点击购买物品后, 游戏服务器就自动运行一条 GM 命令将物品发送到用户游戏角色的邮箱. 在这个例子里 GM 命令的发起端是 Web 服务器, 而运维的时候 GM 命令的发起端可以是任何东西, 例如 VM, Container, Lambda Function 等. 所以我们就需要一套机制能仅让有权限的人或机器远程执行 GM 命令. 这个需求对于长期的正式运营非常重要.

``acore_soap_app`` 项目就是一个针对这个需求的完整解决方案. 它包含两个组件 **Agent** 和 **SDK**.

- **Agent**: 提供了一个部署在游戏服务器 EC2 上的命令行程序, 作为外部 API 调用的桥梁. 使得外部有权限的开发者可以通过 AWS SSM Run Command 远程调用这个命令行程序, 从而实现远程执行 GM 命令.
- **SDK**: 提供了一套远程运行服务器命令的 SDK, 并提供了很多高级功能例如批量执行, 错误处理等功能. 使得开发者可以很方便的编写出基于 GM 命令的应用程序.

在 EC2 上安装完 Agent 之后, 你可以用下面的命令测试.

.. code-block:: bash

    /home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap gm ".server info"


.. _install:

Install
------------------------------------------------------------------------------

``acore_soap_app`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install acore-soap-app

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade acore-soap-app
