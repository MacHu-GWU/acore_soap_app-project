Gadget
==============================================================================
除了 Agent 和 SDK 之外, acore_soap_app 还提供了一些跟 GM 命令相关的小工具, 供运维人员或自动化程序使用.


count_online_players
------------------------------------------------------------------------------
该命令能统计在线玩家数量, 顺便查看一下服务器状态. 任何有需要获取在线玩家数量具体数值的自动化脚本可以利用这个工具.

.. code-block:: bash

    /home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap acsoap canned count-online-players


measure_server_status
------------------------------------------------------------------------------
该命令能测量服务器的在线状态, 并将结果保存到 EC2 实例的 Tags 中. 这个功能可以作为一个 screen 后台无线循环脚本, 每隔 5 分钟运行一次, 以 Tag 的形式给外界通报服务器的运行状态. 由于该函数是本地运行, 不像通过 AWS SSM Run command 有 3-5 秒的延迟, 所以是比较理想的用来监控服务器状态的方法.

.. code-block:: bash

    /home/ubuntu/git_repos/acore_soap_app-project/.venv/bin/acsoap acsoap canned measure-server-status
