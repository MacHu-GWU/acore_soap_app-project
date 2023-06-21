
.. image:: https://readthedocs.org/projects/acore-soap-app/badge/?version=latest
    :target: https://acore-soap-app.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/acore_soap_app-project/workflows/CI/badge.svg
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
魔兽世界服务器 worldserver 自带一个交互式的 Console. GM 可以在里面输入命令来创建账号, 修改密码, 封禁账号等. 你如果用 GM 账号登录游戏, 你也可以在游戏内聊天框输入 GM 命令, 本质是一样的. 但是你需要 SSH 到服务器上才能访问这个 Console 界面, 又或是要登录游戏才能输入 GM 命令, 且这些命令必须要人类手动输入. 简而言之, 这套系统是给人类用的. 但是作为服务器维护者, 你会有需要用程序扫描数据库, 日志分析用户行为, 并且进行自动化维护, 例如封号, 发邮件等等. 这些自动化运维的脚本可能是在游戏服务器上运行, 也可能是在其他地方运行, 例如其他 EC2, 容器, Lambda. 这时我们就需要一套机制能安全地 (仅让有权限的人或机器) 远程执行 GM 命令. 这个需求对于长期的正式运营非常重要. 例如你需要玩家能登录你的服务器官网注册账号, 交易物品等等. 那么你就需要你的官网 Web 服务器能远程执行一些 GM 命令.

该项目是一个针对这个需求的完整解决方案, 它包含两个组件 Agent 和 SDK.

- Agent: 提供了一个部署在游戏服务器 EC2 上的命令行程序, 作为外部 API 调用的桥梁. 使得外部有权限的开发者可以通过 AWS SSM Run Command 远程调用这个命令行程序, 从而实现远程执行 GM 命令.
- SDK: 提供了一套远程运行服务器命令的 SDK, 并提供了很多高级功能例如批量执行, 错误处理等功能. 使得开发者可以很方便的编写出基于 GM 命令的应用程序.


.. _install:

Install
------------------------------------------------------------------------------

``acore_soap_app`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install acore-soap-app

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade acore-soap-app
