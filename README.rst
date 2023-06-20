
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
1. 提供了一个部署在游戏服务器 EC2 上的命令行程序, 作为外部 API 调用的桥梁. 使得外部有权限的开发者可以通过 AWS SSM Run Command 远程调用这个命令行程序, 从而实现远程运行服务器命令.
2. 提供了一套远程运行服务器命令的 SDK, 使得开发者可以很方便的编写出优质的服务器命令程序.


.. _install:

Install
------------------------------------------------------------------------------

``acore_soap_app`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install acore-soap-app

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade acore-soap-app
