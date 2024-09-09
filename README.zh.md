![Website](https://img.shields.io/website?down_color=red&up_color=orange&up_message=hllrcon.app&url=https%3A%2F%2Fhllrcon.app)
![Discord](https://img.shields.io/discord/685692524442026020?color=%237289da&label=discord)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/marechj/hll_rcon_tool)
![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/cericmathey/hll_rcon)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/cericmathey/hll_rcon)
![Docker Pulls](https://img.shields.io/docker/pulls/cericmathey/hll_rcon)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![zh doc](https://shields.io/badge/中文文档-8A2BE2)](README.zh.md)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/T6T83KY8H)

欢迎加入我们的Discord频道，您可以在此获取故障排除帮助和提供反馈，以及其他人间地狱服务器运营的信息：https://discord.gg/hZx6gn3

# 人间地狱（HLL）社区RCON工具 (CRCON)

这是一款由人间地狱玩家社区开发的强大的人间地狱服务器管理工具，旨在取代官方提供的软件，并力争做到遥遥领先。

# 安装指南

## 技术需求

您只需要非常基本的Shell技能，大部分过程只需按照说明操作即可。不过，您需要了解什么是目录（directory，类似于文件夹），如何列出目录的内容，切换目录等。

## 请在安装在虚拟服务器（VPS）而不是您的个人电脑上

CRCON是一个需要时刻运行（24/7）的网站。它会实时抓取服务器的信息并整理，使其可以通过互联网随时被访问。社区玩家和服务器管理员将随时连接和查看。

它实现了分离管理员账户和游戏服务器，并为游戏服务器数据（日志、战绩等）和管理员操作提供了一个集中式数据库。
  - 您无需分享游戏服务器的RCON密码（除非您有充分理由或允许人们越过审计日志），并且应该避免这样做
  - 所有管理员操作都会被记录，以供日后追责

因此，与其在个人电脑上安装，不如租用一个便宜的服务器以支持不间断的运行。

用户也无需安装任何软件，他们只需登录网站即可。

如果您决定将其安装在家用电脑上，请记住您将需要：
- 让电脑24小时不间断运行  
*希望您能忍受嘈杂的风扇声、硬件维护和电费支出；*
- 开放您的互联网访问，包括路由器和防火墙  
*这需要网络管理知识，并可能产生信息安全问题。*

## 硬件需求

- 最低配置：2个CPU核心和6GB的RAM
- 推荐配置：4个CPU核心和8GB的RAM
- 存储空间：如果每天有95+玩家连接，CRCON数据库体积可能会在一年内增长到20GB，它不太能被压缩。因此，我们建议您选择提供超过50GB存储空间的服务。

您可以在只有3GB+的RAM配置上运行，但由于增加VPS的RAM并不容易，最好稍微预留一些。在CRCON中安装使用的服务器越多，您将占用的RAM/CPU/存储空间就越多。

一些服务器供应商提供每月40～50元的新人套餐。

## 软件需求

理论上，您可以在任何可以使用Docker和Docker Compose的地方运行此软件，但除非您有自己的理由，否则您应该使用Linux（任何发行版都应该能够支持。如果您不熟悉，最好选择像Ubuntu或Debian这样更流行的发行版，以便在社区获得技术支持）而不是Windows或任何其他操作系统。

如果您使用除amd64之外的CPU架构，您将无法使用提供的Docker映像。您必须自行构建映像。

如果您在Windows上运行，请不要指望在Discord上有人能提供帮助。

- `git`（可选，但**极度**推荐使用）：https://git-scm.com/downloads  
  如果您不使用git，您只能手动下载并安装以`.zip`格式发布的版本，并且无法像使用git那样轻松地更新您的CRCON。
- `Docker Engine`(社区版)：https://docs.docker.com/engine/install/  
  您也可以使用`Docker Desktop`，但基于您的计算机/服务器/VPS，可能会遇到嵌套虚拟化问题。
- `Docker Compose`：https://docs.docker.com/compose/install/  
注：`docker-compose`已被弃用。  
本自述文件和发布公告将展示Docker Compose的示例。  
*您应该还能够使用docker-compose，但必须相应地调整下面的命令。*   
我们建议您只使用最新的版本，以避免潜在的问题。我们不能保证未来发布的软件能搭配docker-compose正常工作。

一些VPS提供商免费预先安装了Docker的Linux系统实例，请联系他们了解详情。

## 安装步骤

*“我对终端/控制台和代码一无所知，怎么办？”*
- 保持冷静，按部就班。这是一个非常简单的安装过程，许多不太懂技术的人都成功完成了，所以你可能也可以！
- ~~社区还制作了一个百科（感谢[2.Fjg]bn.hall）: https://github.com/MarechJ/hll_rcon_tool/wiki~~  
*（该百科已过时，我们希望我们能尽快安排时间更新它）*
- 大多数Shell命令/错误消息/指南的更详细步骤，都可以通过百度必应谷歌搜索解决，而且CRCON的Discord上已经有了很多常见问题的答案。如果找不到你要找的内容，请在技术支持频道（tech-support）寻求帮助。
- 如果阅读后仍然不明白该怎么做，请在Discord上询问。不过，请您尊重他人的时间和精力，至少先尝试使用百度/其他资源来解决您的问题。

注：以下所有命令都应在类似Debian的包管理模式的Linux终端中使用。

### 1. 下载CRCON

使用SSH客户端（*不知道如何选择？* 试试 https://www.chiark.greenend.org.uk/~sgtatham/putty/ ），通过您的VPS供应商提供的SSH凭据，**以root用户身份**登录到您的远程Linux系统。

在终端中输入以下命令（*按[Enter]回车键确认输入*）：

- 下载CRCON文件：
  > `git clone https://github.com/MarechJ/hll_rcon_tool.git`
- 进入CRCON所在的文件夹：
  > `cd hll_rcon_tool`

### 2. 编辑环境配置文件

现在，您将创建并编辑一个.env文件，在其中告诉CRCON如何连接到您的HLL游戏服务器。

这里我们将使用**nano**，一个在文本模式下运行的简单文本编辑器。  
*您可以使用您喜欢的其他工具，无论是本地工具还是通过SFTP连接获取文件。*

- 复制环境配置文件模版：
  > `cp default.env .env`
- 安装nano文本编辑器（大概率服务器供应商已经提前预装）：
  > `apt-get update && apt-get install nano`
- 启动nano编辑.env文件
  > `nano .env`

在nano中，您可以使用箭头键移动光标。

您不必更改所有的值。只有以下5个是必需的：

1. 选择一个密码，以便CRCON访问数据库。  
  我们无需记住它：您以后不用在任何地方输入它。请参考.env中的注释以避免使用限制字符，如%。  
  在CRCON启动过一次后，请勿更改它：否则您的数据库将无法被访问。

        HLL_DB_PASSWORD=meiyoukonggedemima

3. 输入一个随机混乱的长字符串，用于加密用户密码，您可能希望备份此字符串。  
  如果丢失，您的所有管理员帐户会失效，并且需要重置其密码。  
  在CRCON启动过一次后，请勿更改它：否则您的现有账户会失效。

       RCONWEB_API_SECRET=zheshiyigehenfuzademeiyoukonggedemima
  
我们开始配置您想要添加的游戏服务器（以服务器1 / SERVER 1 为例。您可以根据需要重复以下步骤为第2/3个服务器进行配置）：

3. 输入你的RCON IP（由游戏服务器供应商提供，这于游戏服务器IP不一定相同）：

       HLL_HOST=123.123.123.123

5. 输入服务器的RCON端口（由游戏服务器供应商提供，这于游戏服务器端口不同）：

       HLL_PORT=12345

6. 输入服务器的RCON密码（在游戏服务器供应商门户网站设置）：

       HLL_PASSWORD=fuwuqiderconmima

    请再次确认在`=`前后和您输入的内容里**没有空格**.

7. 退出nano编辑器回到CRCON目录：

    按下`Ctrl + o`保存修改（按Y确认）  
    按下`Ctrl + x`退出nano

### 3. 第一次尝试启动CRCON！

CRCON现在已配置好可以启动并连接到您的HLL游戏服务器。不过，我们后续还有一些步骤，因为我们需要设置用户账户。

注意：启动过程将显示大量的滚动文本。莫慌，因为您不需阅读/执行任何操作，只需静待奇迹的发生。

输入适合您操作系统的命令：

- Linux x86架构：
  > `docker compose up -d --remove-orphans`
- Windows x86架构：
  > `docker volume create redis_data`  
  `docker volume create postgres_data`  
  `docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d`
- 树莓派（Raspberry-Pi，32位）或其他ARM32v7架构：
  > `docker compose -f docker-compose.yml -f docker-compose.arm32v7.yml up -d --build`
- 树莓派（Raspberry-Pi，64位）或其他ARM64v8架构：
  > `docker compose -f docker-compose.yml -f docker-compose.arm64v8.yml up -d --build`

如果一切正常，你会在几分钟后看到一些写着"started"的绿色文字
注：如果你没有为预留的服务器2（SERVER 2）或服务器3（SERVER 3）设置环境参数，在一些行中会出现错误，这是正常的。

如果关于服务器1（xxx _1 -1）的最后几行有显示错误（红色），请检查您在.env文件中的输入，并尝试用上面的启动命令重新启动CRCON。

### 4. 进入CRCON用户界面

您的CRCON界面可以从世界各地的浏览器中访问。  
每个游戏服务器可以单独访问，请注意您.env中每个游戏服务器的RCONWEB_PORT值。  
例如，默认情况下，您可以使用以下方式访问游戏服务器1：http://yourVPSIP:8010/ （将URL中的`yourVPSIP`替换为您的VPS的IP地址）。

- 打开页面并单击菜单中的**LOGIN**。  
- 使用默认的账户/密码 `admin`/`admin` 登陆总管理账户。  
*请先不要碰其他内容，我们还没有设置完成。稍后您有充足的时间探索这个工具。*  
现在，总管理员的密码很不安全，我们必须修改密码。

### 5. 准备配置用户账户

由于内部安全验证，我们需要将VPS的IP和端口声明为“安全”，以便能够进入用户管理工具，否则您将看到CSRF错误。

- 在设置（Settings）菜单中，点击CRCON Settings子菜单，或直接访问 http://yourVPSIP:8010/#/settings/rcon-server

  您将看到一个大块的可编辑文本区域，其中的奇怪代码是格式JSON的配置文本。  
  保持淡定：我们暂时只需要更改其中一行。  

- 修改标着**server_url**的一行：输入你的CRCON网站URL(例如`http://yourVPSIP:8010`）  
你必须用引号（`"`）包裹着URL，并在最后添加一个英文逗号（`,`）。它看起来应该像这样：

      "server_url": "http://yourVPSIP:8010/",

- 点击文本输入区下方的保存按钮（SAVE）  
*(窗口右上角应弹出绿色的确认标志)  
如果弹出黄色或红色标志，则表示您有语法错误：（请查看上面的示例确认设置正确）*

### 6. 重启CRCON

重新启动CRCON的容器。这听起来可能有点奇怪，但这是必需的。  
为了使您刚刚设置的`server_url`值生效，它必须在CRCON Docker容器启动期间进行声明。

    docker compose restart

### 7. 配置用户账户

重启成功后，你便可以在 http://yourVPSIP:8010/admin 配置管理用户了。

您应该已经登陆了总管理账户，否则使用 `admin`/`admin`的用户名和密码登陆。

#### 添加一个新用户

- 点击 **+Add** 按钮
![](images/readme_admin_account_setup_1.png)
- 填写添加用户 **Add User** 的表格  
记得填写用户的Steam 64位ID，这能让CRCON识别一个玩家是否为管理员  
![](images/readme_admin_account_setup_2.png)
- 点击保存 **SAVE** 按钮  
用户创建完成后，您将会看到该页面：![](images/readme_admin_account_setup_3.png)

如果您打算禁用admin帐户，请先为自己添加一个勾选了Superuser status和Staff status的账户！  
除非您把一个用户勾选为管理状态（`staff status`），用户不能自行修改账号密码。

要更改用户密码，请单击其名称，然后单击此链接（如下图）：  
![](images/readme_admin_account_setup_4.png)

用户可以使用专用链接更改当前密码（下方顶部右侧的红色方框）：  
![](images/readme_admin_password_1.png)

#### 修改默认的admin账户的密码

- 点击顶部的 **"Django administration"** 标题回到账户管理页面  
*（和直接进入 http://yourVPSIP:8010/admin 链接效果相同）*
- 点击用户 **Users**，然后选择 **admin**用户
- 修改默认用户密码  
（您也可以通过取消选中“Active”状态来禁用管理员帐户，只需确保另一个用户已提前激活了`Superuser status`和`staff status`）
- 点击保存按钮 **SAVE**

### 8. 基础配置完成

恭喜你！你已经成功为自己搭建了管理游戏服务器的CRCON！

接下来你可以自行探索这个工具的各项功能。

我们明白这个界面设计并不完美。我们很乐意如果有人能加入帮助改善它。

您将在“SETTINGS”菜单中找到许多可以自定义的内容，大多数设置在其各自的页面上都有一些解释。

如果您有任何问题，请随时在CRCON Discord上提问。

玩得开心！

---

您可以选择捐赠以支持和帮助我们  
获取的资金会用于激励开发人员和内容创建者  
以开发更多的教学视频、文档、功能等

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=56MYGQ2966V7J)

---

# 更新到最新版本

请加入CRCON Discord并关注我们的公告。  
有时，更新说明指引会与标准的指引不同。  
如果您正在从旧版本更新，请按顺序查看公告，并跟着进行任何非标准更改。

### 标准更新（适合大多数情况）

- 从GitHub下拉更新
  > `git fetch --tags`
- 切换到标记的发布版本
  > `git checkout v9.4.1`
- 获取最新的Docker镜像
  > `docker compose pull`
- 重新启动您的容器
  - Linux x86架构
    > `docker compose up -d --remove-orphans`
  - Windows x86架构
    > `docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d --remove-orphans`
  - 树莓派（Raspberry-Pi，32位）或其他ARM32v7架构
    > `docker compose -f docker-compose.yml -f docker-compose.arm32v7.yml up --build -d --remove-orphans`
  - 树莓派（Raspberry-Pi，64位）或其他ARM64v8架构
    > `docker compose -f docker-compose.yml -f docker-compose.arm64v8.yml up --build -d --remove-orphans`

您也可以通过手动下载[最新版压缩包](https://github.com/MarechJ/hll_rcon_tool/releases/latest)来更新（不推荐）

**注**：如果在拉取时出现git错误消息，则必须解决这些错误才能升级。这种情况通常不会发生，除非你一直在修在源文件。  
**注**：每次都获取源代码或获取docker-compose文件非常重要，因为新版本可能已经引入了新的依赖项。

# 回退到旧版本（出现问题时）

在Docker Hub（或GitHub）上查看可用的版本号：  
https://hub.docker.com/r/cericmathey/hll_rcon/tags  
https://github.com/MarechJ/hll_rcon_tool/releases

编辑您的.env文件，并将TAGGED_VERSION从latest更改为特定的标记版本。它必须与Docker Hub上的发布标记匹配，例如：

    TAGGED_VERSION=9.4.1

# 使用教程

*即将推出展示视频*

有一个公开API端点可供任何人在 http://yourVPSIP:7010/api/scoreboard 上无需密码使用。

有关如何使用该应用程序的某些功能的信息，请参阅 [用户手册](USERGUIDE.md) 。