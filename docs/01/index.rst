Access Game Server Console Remotely
==============================================================================


1. 背景信息
------------------------------------------------------------------------------
**GM 命令是如何被执行的**

启动魔兽世界服务器的本质是启动 ``bin/authserver`` 登录服务器和 ``bin/worldserver`` 世界服务器. 其中世界服务器自带一个交互式的 Console 命令行界面, 你可以在里面输入 GM 命令, 例如创建账号, 封号等. 类似的, 你如果用 GM 账号登录游戏, 你也可以在游戏内聊天框输入 GM 命令, 本质是一样的.

**为什么需要远程执行 GM 命令**

但是你需要 SSH 到服务器上才能访问这个 Console 界面, 又或是要登录游戏才能输入 GM 命令, 且这些命令必须要人类手动输入. 简而言之, 这套系统是给人类用的. 但是作为服务器维护者, 你会有需要用程序扫描数据库, 日志分析用户行为, 并且进行自动化维护, 例如封号, 发邮件等等. 这些自动化运维的脚本可能是在游戏服务器上运行, 也可能是在其他地方运行, 例如其他 EC2, 容器, Lambda. 这时我们就需要一套机制能安全地 (仅让有权限的人或机器) 远程执行 GM 命令. 这个需求对于长期的正式运营非常重要. 例如你需要玩家能登录你的服务器官网注册账号, 交易物品等等. 那么你就需要你的官网 Web 服务器能远程执行一些 GM 命令.

幸运的是 Azerothcore 自带了一套解决方案. 下面我们来看看这套方案的基本原理, 以及如何使用.


2. 基本原理
------------------------------------------------------------------------------
`SOAP <https://en.wikipedia.org/wiki/SOAP>`_ 是一个基于 XML 的远程访问协议. 你可以给他发送一个 XML 请求, 里面包含了 GM 命令, 服务器会执行这个命令, 并返回执行结果.

他是一个很简单的协议, 跟 HTTPS 不同, 数据在传输过程中是以明文传输, 可以被截获. 这就意味着这个 SOAP 服务一定要运行在本地. 你如果在游戏服务器上再运行一个 SOAP 服务器进程, 然后向公网打开端口, 那么你所有对 SOAP 的请求都可以被截获, 这会造成巨大的安全隐患, **请千万不要这么做**.

游戏服务器自带 SOAP 服务器功能, 不过默认是关闭的. 你可以在 ``worldserver.conf`` 文件中设置 ``SOAP.Enabled = 1`` (搜索 ``SOAP.Enabled``) 即可. 默认会在 ``127.0.0.1:7878`` 开放一个 SOAP 服务器. 因为首先 SOAP 只对本地开放, 公网无法对其访问, 而且我们的 security group 没有给外网允许 7878 端口, 所以这样做是完全安全的.

换言之, 如果你已经 SSH 到了 EC2 上, 那么你用 ``curl 127.0.0.1.7878 ...`` 就可以通过 SOAP 执行 GM 命令了.

Reference:

- `Azeroth Core 关于远程访问的官方文档 <https://www.azerothcore.org/wiki/remote-access>`_: 里面详细介绍了 SOAP 的设置, 鉴权, 以及 XML 语法.


3. 一个简单的例子
------------------------------------------------------------------------------
比如我们要运行 ``server info`` 命令查询服务器信息. 那么首先我们先 SSH 到 EC2 里, 然后在 EC2 上创建一个 ``sample.xml`` 文件作为模板, 把下面的内容复制粘贴进去. 其中 ``{command}`` 这部分是给 Python 预留的字符串模板.

.. code-block:: xml

    <SOAP-ENV:Envelope
        xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
        xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
        xmlns:xsd="http://www.w3.org/1999/XMLSchema"
        xmlns:ns1="urn:AC">
        <SOAP-ENV:Body>
        <ns1:executeCommand>
            <command>{command}</command>
        </ns1:executeCommand>
        </SOAP-ENV:Body>
    </SOAP-ENV:Envelope>

然后我们可以写一个 Python 脚本, 用 `requests <https://pypi.org/project/requests/>`_ 库来执行命令. 我们可以在 ``sample.xml`` 旁边创建一个 ``sample.py`` 脚本, 运行这段代码, 你就会看到程序打印的服务器信息, 这和你在 Console 内输入 ``server info`` 是一摸一样的. 具体代码如下:

.. code-block:: python

    # -*- coding: utf-8 -*-

    import requests
    from pathlib import Path

    # the in game GM account username and password
    username = "admin"
    password = "admin"
    # the command you want to execute
    command = "server info"

    # the SOAP server url
    url = f"http://{username}:{password}@localhost:7878/"
    # HTTP headers
    headers = {
        "Content-Type": "application/xml"
    }
    # locate the xml template
    path_xml = Path(__file__).absolute().parent.joinpath("sample.xml")
    # build the final XML request
    xml = path_xml.read_text(encoding="utf-8").format(command=command)

    # send the request
    res = requests.post(url, headers=headers, data=xml)

    # print response
    print(res.text)

基于这个例子, 这样我们只要修改 ``command = "..."`` 的部分就可以执行我们任何想要的命令而无需打开控制台了.

这里有一个小地方需要注意, 有很多 GM 命令是需要用双引号把字符串包裹起来的, 拿这个邀请人入工会的命令来说: ``.guild invite [$CharacterName] "$GuildName"``, 正确的格式是 ``guild invite [charname] "guildname"``. 这时候你的 Python 代码中就要改为 ``command = "guild invite [charname] \"guildname\""``.

Reference:

- `Azeroth Core GM 命令列表 <https://www.azerothcore.org/wiki/gm-commands>`_


4. 实现远程执行的软件架构
------------------------------------------------------------------------------
前面的 "远程执行" 实际上是先 SSH 到服务器上, 然后用 SOAP 来调用同样位于本地的服务器命令. 而真正的 "远程执行" 是指的完全不同的一台电脑上执行. 我们来





这里我建议使用 AWS SSM remote command 来远程执行, 详情可以参考 :ref:`run-remote-command-on-ec2-via-ssm`. 因为最麻烦的是如何确保请求执行命令的人有合适的权限跟这台游戏服务器的 EC2 通信? 要知道这个 EC2 是用来服务玩家的, 而不是一个 API 服务器, 如果你要在这个 EC2 上部署一个 API 服务器或是在同一个网络专门部署一台代理服务器, 那就太麻烦了, 而且很容易做的不好出现安全问题. 而 AWS SSM 是使用的 IAM Role, 所有的命令, 数据在传输过程中都是加密的, 非常的安全.

所以你只要在 EC2 上用 Python 把之前的那个例子改改, 包装成一个命令行工具即可, 然后用 AWS SSM 远程运行这个命令行工具即可. 这样就可以在任何地方远程执行 GM 命令了. 之后我们会给出一个具体的例子.

