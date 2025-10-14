

# Linux & 云计算运维面试题复习资料

[TOC]

## 第一部分：Rocky Linux 9 基础工具与配置

### 1.1 rsync 相关

#### 1.1.1 rsync 有哪些特点？

* 增量传输：仅传源与目标的差异部分，节省带宽；

* 多协议支持：本地文件、SSH、rsync 协议（daemon 模式）；

* 数据压缩：传输中自动压缩，提升效率；

* 保持文件属性：同步权限、所有者、时间戳等元数据；

* 灵活删除：支持 `--delete` 保持源目一致；

* 断点续传：中断后可继续传输。

#### 1.1.2 rsync --delete 参数的作用是什么？使用时有什么风险？

* 作用：使目标目录与源目录完全一致，删除目标中源不存在的文件 / 目录；

* 风险：若源目录误删文件，目标会同步删除，导致数据丢失；建议先 `--dry-run` 模拟，或备份目标目录。

#### 1.1.3 rsync 在使用 rsync 协议时，如何实现免密传输？

1. 服务器端：

* 编辑 `/etc/rsyncd.conf`，配置 `auth users = 用户名`、`secrets file = /etc/rsyncd.secrets`；

* 创建 `/etc/rsyncd.secrets`（格式：`用户名:密码`），权限设为 `600`；

* 重启 rsync 服务：`systemctl restart rsyncd`。

1. 客户端：

* 创建密码文件（仅写密码），权限 `600`；

* 传输命令：`rsync -av --password-file=密码文件 用户名@服务器IP::模块名 /本地目录`。

#### 1.1.4 rsync 已设置正确账号密码，传输时仍提示密码错误，可能原因？

* 密码文件权限非 `600`（rsync 视为不安全）；

* 密码文件格式错误（服务端需 `用户名:密码`，客户端仅密码）；

* `rsyncd.conf` 中 `auth users` 与实际用户名不匹配；

* 服务端配置未生效（未重启 rsyncd 或 `exportfs -r`）；

* 客户端指定的模块名与 `rsyncd.conf` 中 `[模块名]` 不一致。

### 1.2 cron 定时任务相关

#### 1.2.1 cron 定时任务执行时提示 command not found，原因及解决？

* 原因：cron 默认 `PATH` 仅含 `/usr/bin:/bin`，命令不在此路径则无法识别；

* 解决：

1. 用命令绝对路径（如 `/usr/local/bin/rsync`）；

2. 脚本开头设 `PATH`：`export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin`；

3. crontab 中直接定义 `PATH`（如 `PATH=/usr/local/bin:...`）。

#### 1.2.2 Linux 中如何配置一个定时任务？

1. 编辑当前用户定时任务：`crontab -e`（首次选编辑器）；

2. 按格式添加：`分 时 日 月 周 命令`（例：`0 2 * * * /path/``backup.sh` 每天凌晨 2 点执行）；

3. 保存退出自动生效，无需重启 cron；

4. 查看任务：`crontab -l`；删除所有任务：`crontab -r`。

#### 1.2.3 定时任务执行报错，排查思路？

1. 查日志：任务输出日志（如 `/var/log/backup.log`）或系统日志 `/var/log/cron`；

2. 验命令：手动执行任务中的命令 / 脚本，确认是否报错；

3. 检查路径：用绝对路径，避免相对路径；

4. 权限问题：脚本设执行权限（`chmod +x`），cron 用户有文件访问权；

5. 环境变量：脚本中显式设 `PATH` 或必要环境变量；

6. 语法错误：crontab 中 `%` 需转义为 `\%`。

#### 1.2.4 定时任务 `0 2 * * * /path/to/``backup.sh`` >/var/log/backup_$(date +%Y%m%d).log 2>&1` 执行报错，原因及解决？

* 原因：crontab 中 `%` 是特殊字符（表换行），`date +%Y%m%d` 中的 `%` 未转义；

* 解决：`%` 转义为 `\%`，修改为：

  `0 2 * * * /path/to/``backup.sh`` >/var/log/backup_$(date +\%Y\%m\%d).log 2>&1`

#### 1.2.5 编写定时任务：每分钟巡检服务器 load 值，追加到文件？

`*/1 * * * * uptime >> /var/log/server_load.log 2>&1`

（`uptime` 输出 1/5/15 分钟负载，追加到日志）

#### 1.2.6 编写定时任务：每分钟巡检服务器可用内存值，追加到文件？

`*/1 * * * * free -h | awk '/Mem:/ {print "["$(date +\%Y\%m\%d_\%H\%M\%S)"] 可用内存: " $4}' >> /var/log/available_memory.log 2>&1`

（`free -h` 查内存，`awk` 提取可用内存并加时间戳）

### 1.3 服务器进程与权限

#### 1.3.1 如何让程序在后台运行？

1. 命令后加 `&`：`command &`（退出终端可能终止）；

2. `nohup`：`nohup command &`（忽略挂断信号，日志默认存 `nohup.out`）；

3. `screen/tmux`：`screen -S 会话名`，执行命令后按 `Ctrl+A+D` 脱离，关闭终端仍运行；

4. systemd 服务：配置 `/etc/systemd/system/` 服务文件，`systemctl start` 启动，支持开机自启。

#### 1.3.2 解释 umask 与 ACL？

* **umask**：文件 / 目录创建时的默认权限掩码，计算方式：默认权限（目录 777、文件 666）- umask 值；例 `umask 022` 时，目录 755、文件 644。

* **ACL（Access Control Lists）**：细粒度权限控制，支持对特定用户 / 组设权限（超传统 ugo）；

  * 查看：`getfacl 文件名`；

  * 设置：`setfacl -m u:用户名:rwx 文件名`（给用户读写执行权）。

### 1.4 SSH 登录问题排查

#### 1.4.1 客户端通过 SSH 登录服务器，telnet 22 正常但提示密码错误，如何排障？

1. 验证密码：确认密码正确（注意大小写，关闭 Caps Lock）；

2. 查日志：服务器 `/var/log/secure` 看具体错误（如 `Permission denied`）；

3. 用户状态：`passwd -S 用户名` 查是否锁定（锁定状态为 `L`），解锁：`passwd -u 用户名`；

4. SSH 配置：检查 `/etc/ssh/sshd_config` 中 `AllowUsers`/`DenyUsers` 是否限制，需重启 sshd；

5. PAM 配置：检查 `/etc/pam.d/sshd` 是否有异常限制（如密码复杂度）。

### 1.5 Jpress 访问问题排查

#### 1.5.1 Jpress 服务器内部可访问，本地无法访问，如何排查？

1. 端口与防火墙：

* 查端口是否开放：`firewall-cmd --list-ports`，未开放则 `firewall-cmd --add-port=80/tcp --permanent` 并重启防火墙；

1. SELinux：

* 临时关闭测试：`setenforce 0`，若可访问则设规则：`setsebool -P httpd_can_network_connect 1`；

1. 绑定地址：

* 查 Jpress 配置，确保绑定 `0.0.0.0`（允许所有 IP），而非 `127.0.0.1`（仅本地）；

1. 网络与路由：

* 本地 `telnet 服务器IP 端口`，不通则查路由或中间设备（如路由器端口映射）。

## 第二部分：NFS 技术相关

### 2.1 NFS 安全性判断

#### 2.1.1 “telnet 和 NFS 传输都是安全的” 说法是否正确？

* 不正确；

  * telnet：数据明文传输（含用户名 / 密码），极不安全；

  * NFS：NFSv3 及之前无加密，NFSv4 默认不加密，整体安全性低。

### 2.2 NFS 权限控制

#### 2.2.1 NFS 如何做权限控制？

1. `exports` 配置：编辑 `/etc/exports`，例：`/shared ``192.168.1.0/24(rw,sync,root_squash)`；

* `rw`/`ro`：读写 / 只读；`root_squash`：客户端 root 映射为服务器 nfsnobody；`all_squash`：所有客户端用户映射为 nfsnobody；

1. 文件系统权限：依赖底层 chmod/chown，客户端用户 ID 需与服务器一致（或通过 idmapd 映射）；

2. 结合 ACL：对共享目录设 ACL，实现细粒度控制。

### 2.3 NFS 挂载 / 卸载问题排查

#### 2.3.1 NFS 无法挂载，常见问题及解决？

1. 服务未启动：查 `nfs-server`/`rpcbind` 状态：`systemctl status nfs-server rpcbind`，未启动则启动；

2. `exports` 配置错误：查语法，`exportfs -r` 生效，`exportfs -v` 看生效共享；

3. 网络问题：客户端 ping 服务器，防火墙开放 NFS 端口（111、2049，或 `firewall-cmd --add-service=nfs --permanent`）；

4. 权限不足：客户端用户无共享目录访问权，调整服务器目录权限或 `exports` 的 squash 参数；

5. SELinux 限制：临时关 `setenforce 0`，可用则设规则：`setsebool -P nfs_export_all_rw 1`。

#### 2.3.2 NFS 无法卸载，排障思路？

1. 进程占用：`fuser -m /mount/path` 或 `lsof /mount/path` 查占用进程，结束后卸载；

2. 强制卸载：懒卸载（后台释放）：`umount -l /mount/path`；强制卸载：`umount -f /mount/path`；

3. 子目录挂载：先卸载挂载点下的子目录。

### 2.4 NFS 适用场景

#### 2.4.1 哪些场景下使用 NFS？

* 局域网服务器集群共享静态资源（如 Web 服务器共享图片 / JS/CSS）；

* 虚拟机与宿主机共享文件（开发环境）；

* 备份服务器集中获取多客户端数据；

* 需频繁访问共享文件且实时性要求不高的场景。

## 第三部分：Python 生态相关

### 3.1 Python 虚拟环境

#### 3.1.1 Python 生态中 venv、miniconda 是什么？作用及区别？

* **venv**：Python 3.3+ 内置轻量虚拟环境工具，仅管理 Python 解释器和 pip 库，隔离项目依赖；

* **miniconda**：轻量 conda 包管理器，可创建隔离环境，同时管理 Python 版本和跨语言包（如 C/C++ 库）；

* 区别：venv 仅 Python 相关，miniconda 功能更强（支持多语言包、版本管理）。

#### 3.1.2 Python 为什么要用虚拟环境？解决什么问题？

* 解决依赖冲突：不同项目用不同版本库（如项目 A 用 Django 2.x，项目 B 用 3.x）；

* 隔离系统环境：避免污染系统 Python 全局库，不影响系统工具；

* 简化部署：生成 `requirements.txt`，便于其他环境重建依赖。

### 3.2 进程管理工具

#### 3.2.1 gunicorn 是什么？作用？

* Python 的 WSGI HTTP 服务器，用于运行 Django/Flask 等 Web 应用；

* 作用：处理 HTTP 请求并转发给应用，支持多进程 / 线程，提升并发能力。

#### 3.2.2 supervisord 是什么？作用及使用步骤？

* **作用**：进程管理工具，监控进程状态（意外退出自动重启），集中管理多进程（如 gunicorn、爬虫），记录日志；

* **使用步骤**：

1. 安装：`pip install supervisor`；

2. 生成配置：`echo_supervisord_conf > /etc/supervisord.conf`；

3. 配置进程（编辑 `/etc/supervisord.conf`）：

```

\[program:myapp]

command=/path/venv/bin/python /path/app.py  # 启动命令

autostart=true  # 开机自启

autorestart=true  # 意外退出重启

stdout\_logfile=/var/log/myapp.log  # 输出日志

```

1. 启动服务：`supervisord -c /etc/supervisord.conf`；

2. 管理进程：`supervisorctl -c /etc/supervisord.conf start/stop/restart myapp`。

#### 3.2.3 systemctl start supervisord 启动报错，如何排查？

1. 配置语法错误：`supervisord -t -c /etc/supervisord.conf` 检查；

2. 日志权限：确保 `stdout_logfile` 路径可写（改权限或所有者）；

3. 端口冲突：默认 9001 端口，改 `[inet_http_server]` 的 `port`；

4. 进程已启动：`ps aux | grep supervisord`，kill 后重启；

5. 系统日志：`journalctl -u supervisord` 查详细错误。

#### 3.2.4 supervisord 适用场景？

* 长期运行的后台服务（如 Flask/Django、Celery Worker）；

* 无自启动能力的脚本（如自定义监控脚本）；

* 集中管理多进程（避免逐一手动启动）。

#### 3.2.5 gunicorn、supervisord、miniconda、venv 之间的关系？

* venv/miniconda 用于环境隔离（venv 轻量，miniconda 强功能）；

* gunicorn 是 Web 应用服务器，需在虚拟环境中安装启动；

* supervisord 管理 gunicorn 等进程（崩溃自动重启），形成 “虚拟环境→应用→服务器→进程管理” 协作链。

### 3.3 pip 与多 Python 版本

#### 3.3.1 pip 是什么？下载的数据存放在哪个目录？

* **作用**：Python 包管理工具，安装 / 卸载 / 升级第三方库（如 `pip install requests`）；

* **存储目录**：默认存 `site-packages`；

  * 系统 Python：`/usr/lib/pythonX.Y/site-packages`（X.Y 为版本，如 3.9）；

  * 虚拟环境：`/path/venv/lib/pythonX.Y/site-packages`。

#### 3.3.2 Linux 中如何同时拥有多个 Python 版本？

1. pyenv 工具：

* 安装：`curl ``https://pyenv.run`` | bash`；

* 安装版本：`pyenv install 3.9.10`；

* 切换版本：`pyenv local 3.9.10`（当前目录）；

1. 手动编译：源码编译安装到不同目录（如 `/usr/local/python3.8`），通过绝对路径调用；

2. 系统包管理器：`yum install python3.8 python3.9`（部分发行版支持）；

3. 容器隔离：Docker 运行不同 Python 版本容器，完全隔离。

## 第四部分：HTTP & 网络基础

### 4.1 DNS 与网络流程

#### 4.1.1 浏览器访问一个域名的过程？

1. DNS 解析：浏览器→操作系统→本地 DNS→根→顶级域→权威 DNS，获取 IP；

2. 建立连接：TCP 三次握手（80/443 端口），HTTPS 需 TLS 握手；

3. 发送请求：浏览器发 HTTP 请求（方法、路径、头信息）；

4. 服务器响应：返回 HTTP 响应（状态码、头、体）；

5. 渲染页面：解析 HTML/CSS/JS，加载资源，展示页面；

6. 关闭连接：TCP 四次挥手（或保持长连接）。

#### 4.1.2 DNS 解析设置中，常见解析类型及含义？

* A 记录：域名→IPv4 地址（如 `example.com``→``192.168.1.1`）；

* AAAA 记录：域名→IPv6 地址；

* CNAME 记录：域名→另一个域名（别名，如 `www→``example.com`）；

* MX 记录：指定邮件服务器（含优先级，如 `example.com``→``mail.example.com``，优先级10`）；

* NS 记录：指定管理域名的 DNS 服务器；

* TXT 记录：存储文本（如 SPF 反垃圾邮件）；

* SRV 记录：指定服务位置（协议、端口，如 VoIP）。

#### 4.1.3 什么是 A 记录、CNAME 记录？

* A 记录：将域名直接映射到 IPv4 地址，基础解析类型；

* CNAME 记录：将域名映射到另一个域名（别名），用于域名跳转或 CDN 配置（无需关心源站 IP 变化）。

#### 4.1.4 公司的网络支持 IPv6 吗？如何确认？

* 取决于基础设施配置，确认方式：

1. 查服务器 IPv6 地址：`ip -6 addr`（有 `inet6` 开头则支持）；

2. 测试连通性：`ping6 2001:4860:4860::8888`（ping 谷歌 IPv6 DNS，通则支持）；

3. 查网络设备（路由器 / 防火墙）是否启用 IPv6，ISP 是否提供 IPv6 线路。

### 4.2 TCP 协议基础

#### 4.2.1 什么是 TCP 三次握手？

* 建立可靠连接的过程，确保双方收发能力正常：

1. 客户端发 `SYN` 包：“我要连接，初始序列号 X”；

2. 服务器回 `SYN+ACK` 包：“收到，我的序列号 Y，确认收到 X”；

3. 客户端发 `ACK` 包：“收到 Y，连接建立”；

* 完成后开始传输应用层数据。

### 4.3 Session 与 Cookie

#### 4.3.1 Session 和 Cookie 的区别？Cookie 的特性（只读、过期时间、大小限制、跨域）？

| 特性   | Cookie                          | Session                             |
| ---- | ------------------------------- | ----------------------------------- |
| 存储位置 | 客户端（浏览器文件 / 内存）                 | 服务器端（内存 / 数据库）                      |
| 安全性  | 低（明文，可篡改）                       | 高（仅通过 SessionID 关联）                 |
| 大小限制 | 约 4KB（浏览器限制）                    | 无明确限制（取决于服务器存储）                     |
| 过期时间 | 可设 `Max-Age`（秒）/`Expires`（绝对时间） | 服务器设超时（如 30 分钟无活动）                  |
| 读取限制 | `HttpOnly` 则 JS 无法读取（防 XSS）     | 客户端无法直接访问                           |
| 跨域支持 | 受 SameSite 属性限制（默认 Lax）         | 依赖 Cookie 传 SessionID，同 Cookie 跨域限制 |

### 4.4 HTTP 协议核心

#### 4.4.1 HTTP 协议中常见的状态码？

* 1xx（信息）：`100 Continue`（客户端可继续发请求）；

* 2xx（成功）：`200 OK`（成功）、`201 Created`（资源创建）、`204 No Content`（无响应体）；

* 3xx（重定向）：`301 永久重定向`、`302 临时重定向`、`304 Not Modified`（用缓存）；

* 4xx（客户端错）：`400 请求格式错`、`401 未认证`、`403 权限不足`、`404 资源不存在`、`405 方法不支持`；

* 5xx（服务器错）：`500 内部错`、`502 Bad Gateway`（网关错）、`503 服务不可用`、`504 网关超时`。

#### 4.4.2 HTTP 协议中，有哪些常见请求头？

* Host：指定请求域名 + 端口（如 `Host: ``example.com:8080`）；

* User-Agent：客户端标识（浏览器 / 设备信息）；

* Accept：可接受的响应数据类型（如 `text/html, application/json`）；

* Accept-Encoding：支持的压缩算法（如 `gzip, deflate`）；

* Accept-Language：偏好语言（如 `zh-CN, en-US`）；

* Cookie：客户端发送的 Cookie 键值对；

* Authorization：身份认证信息（如 `Bearer token`、`Basic base64`）；

* Content-Type：请求体数据类型（如 `application/json, multipart/form-data`）；

* Referer：请求来源 URL（防盗链用）；

* Origin：跨域请求的源（协议 + 域名 + 端口）；

* Cache-Control：缓存策略（如 `no-cache`、`max-age=3600`）。

#### 4.4.3 什么是 ACME 协议？

* ACME（Automatic Certificate Management Environment）：自动化 SSL/TLS 证书管理协议；

* 作用：实现证书全自动签发、续期、吊销，无需人工干预；

* 应用：Let's Encrypt 基于 ACME 提供免费证书，配合 Certbot 自动完成配置（默认 90 天续期）。

### 4.5 性能与部署

#### 4.5.1 什么是 PV、UV？

* PV（Page View）：页面浏览量，用户打开 / 刷新一次页面计 1 次；

* UV（Unique Visitor）：独立访客，一定时间内（如 1 天）访问的独立用户数（按 IP/Cookie 识别，同一用户多次访问计 1 次）。

#### 4.5.2 你的网站支持多少并发数？QPS？Tomcat 相关？

* 并发数：同时处理的请求连接数（如服务器同时承载 1000 个连接）；

* QPS（Queries Per Second）：每秒处理的请求数（反映处理能力）；

* Tomcat：默认并发数 100-200，可通过 `server.xml` 的 `maxThreads` 调整（建议 200-1000，取决于 CPU / 内存）；优化后单实例 QPS 可达数千。

#### 4.5.3 对后端接口做 CDN 加速会有什么问题？静态资源做 CDN 加速后，发版如何刷新缓存？

* **后端接口 CDN 问题**：

1. 接口返回动态数据（如用户信息），CDN 缓存导致数据不一致；

2. 缓存策略复杂，易引发穿透 / 击穿；

* **静态资源刷新缓存**：

1. 主动刷新：CDN 控制台手动刷 URL / 目录（立即生效，适合少量文件）；

2. 版本控制：资源名加哈希（如 `app.123.js`），发版更新文件名，避免缓存；

3. 缓存策略：设 `max-age`，结合 `ETag`/`Last-Modified` 实现条件请求。

#### 4.5.4 前端工程有哪些部署方案？

* Nginx 部署：静态文件放 Nginx 目录，Nginx 提供 HTTP 服务（支持 Gzip、缓存）；

* CDN + 对象存储：资源传 S3/OSS/COS，结合 CDN 加速（降源站压力，提访问速度）；

* Docker 容器化：前端打包为镜像，容器运行（环境一致，CI/CD 集成）；

* Serverless 部署：部署到 Vercel/Netlify/ 阿里云 FC，无需管理服务器。

### 4.6 工程实践

#### 4.6.1 为什么要将配置与代码分离？好处是什么？

* 环境隔离：开发 / 测试 / 生产配置（如数据库地址、密钥）独立，避免硬编码差异；

* 安全加固：敏感信息（密码 / Token）不进代码仓库，降低泄露风险；

* 灵活修改：配置变更无需改代码 / 重部署（如调超时时间）；

* 便于维护：集中管理（如配置中心），支持动态更新，符合 DevOps 流程。

#### 4.6.2 如何查看 inode？

* 单个文件 inode 号：`ls -i 文件名`（如 `ls -i test.txt`）；

* 文件系统 inode 总使用情况：`df -i`（显示分区 inode 使用率）；

* 文件详细 inode 信息（权限 / 所有者 / 时间戳）：`stat 文件名`（如 `stat test.txt`）。

#### 4.6.3 在公司遇见搞不定的任务怎么办？

1. 拆解问题：拆分为小步骤，定位卡点（如 “接口超时”→“网络 / 数据库 / 代码逻辑”）；

2. 主动调研：查官方文档、Stack Overflow、内部知识库，找同类方案；

3. 寻求帮助：向同事请教，清晰描述背景、已尝试方案、困境；

4. 向上反馈：长时间无进展时，向领导说明情况，明确需资源（人力 / 工具）或调优先级；

5. 记录总结：解决后整理文档，避免重复踩坑。

## 第五部分：Nginx 基础

### 5.1 Nginx 错误排查

#### 5.1.1 某系统用 Nginx 做接入层，打开页面出现 502 Bad Gateway，如何排查？

* 502 表示 Nginx 无法从后端获取有效响应，排查步骤：

1. 查后端服务状态：`systemctl status 服务名`（如 Tomcat），停止则重启；

2. 验网络连通性：Nginx 服务器上 `telnet 后端IP 端口`/`curl 后端IP:端口`，不通则查防火墙 / 路由；

3. 查 Nginx 配置：`proxy_pass` 指向的后端地址 / 端口是否正确；

4. 查后端负载：后端 CPU / 内存过高、连接数满（如 Tomcat `maxThreads` 耗尽），需优化资源 / 扩容；

5. 分析日志：Nginx 错误日志 `/var/log/nginx/error.log` + 后端服务日志，定位具体错误。

### 5.2 Nginx 进程模型

#### 5.2.1 解释 Nginx 的进程模型（Master-Worker 模型）？

* 多进程模型：1 个 Master 进程 + 多个 Worker 进程；

1. Master 进程（管理）：加载配置、启动 / 停止 Worker、接收外界信号（如 `reload`）、监控 Worker 状态（异常退出自动重启）；

2. Worker 进程（处理请求）：实际处理客户端 HTTP 连接 / 数据转发，平等竞争请求，共享内存同步信息；

* 优势：高并发（Worker 独立，一个异常不影响其他）、热部署（`nginx -s reload` 零停机更新）。

#### 5.2.2 Nginx 配置文件中，worker\_processes 的作用？

* 用于设置 Worker 进程数量，例：`worker_processes 4;`；

* 作用：控制 Nginx 处理请求的进程数，影响并发能力；

* 最佳实践：设为 CPU 核心数（或 `auto` 自动匹配），避免进程过多导致 CPU 上下文切换开销。

### 5.3 Nginx 核心配置

#### 5.3.1 Nginx 的负载均衡策略有哪些？

* 轮询（默认）：请求按顺序分配，适合服务器性能相近；

* weight（权重）：按权重分配（值越大优先级高），适合性能不均，例：

```

upstream tomcat\_servers {

         server 192.168.1.10 weight=3;  # 30%请求

         server 192.168.1.11 weight=7;  # 70%请求

}

```

* ip\_hash：按客户端 IP 哈希分配，确保同一客户端访问同一服务器（会话保持）；

* least\_conn：优先分配给连接数最少的服务器，适合请求处理时间差异大；

* url\_hash（第三方模块）：按请求 URL 哈希分配，适合静态资源缓存。

#### 5.3.2 如何实现动静分离？（结合配置说明）

* 动静分离：动态请求（API/JSP）与静态资源（图片 / CSS/JS）分开处理，配置例：

```

server {

         listen 80;

         server\_name www.example.com;

         \# 动态请求：代理到后端 Tomcat

         location /api/ {

             proxy\_pass http://tomcat\_servers;

         }

         \# 静态请求：Nginx 直接处理，设缓存

         location \~\* \\.(gif|jpg|jpeg|png|css|js|ico)\$ {

             root /usr/share/nginx/html/static;  # 静态资源目录

             expires 30d;  # 浏览器缓存 30 天

         }

         \# 根目录（静态页面）

         location / {

             root /usr/share/nginx/html;

             index index.html index.htm;

         }

}

```

### 5.4 Nginx 性能优化

#### 5.4.1 Nginx 的性能优化方法？

* 进程配置：`worker_processes auto;`（匹配 CPU 核心）；`worker_connections 10240;`（单个 Worker 最大连接数，需调大 `ulimit -n`）；

* 事件模型：启用 `epoll`（Linux 高效 I/O）：

```

events {

         use epoll;

         worker\_connections 10240;

}

```

* 连接优化：设超时时间，避免连接长期占用：

```

keepalive\_timeout 60;  # 长连接超时

client\_header\_timeout 10;  # 读请求头超时

```

* 压缩与缓存：启用 Gzip，配置浏览器缓存：

```

gzip on;

gzip\_types text/css application/javascript;

location \~\* \\.(js|css)\$ { expires 7d; }

```

* CPU 亲和性：绑定 Worker 到特定 CPU 核心，减少切换开销：

```

worker\_cpu\_affinity 0001 0010 0100 1000;  # 4 核 CPU

```

### 5.5 链接区别

#### 5.5.1 软链接和硬链接有什么区别？

| 特性       | 硬链接（Hard Link）           | 软链接（Symbolic Link） |
| -------- | ------------------------ | ------------------ |
| inode 关联 | 与源文件共享同一个 inode          | 独立 inode，内容是源文件路径  |
| 源文件删除后   | 仍可访问（链接计数减 1，不为 0 则文件存在） | 失效（路径不存在）          |
| 跨文件系统    | 不支持（inode 仅同一文件系统唯一）     | 支持（路径可跨分区）         |
| 指向对象     | 仅文件，不能指向目录               | 可指向文件或目录           |
| 创建命令     | `ln 源文件 链接文件`            | `ln -s 源文件 链接文件`   |

## 第六部分：Nginx\&Keepalived 高可用

### 6.1 Keepalived 基础

#### 6.1.1 Keepalived 是如何实现高可用的？

* 基于 VRRP（虚拟路由冗余协议），核心逻辑：

1. 主节点（Master）和备节点（Backup）共享一个虚拟 IP（VIP），对外提供服务的是 VIP；

2. 主节点定期向备节点发送 VRRP 心跳广播，告知自身状态；

3. 备节点长时间未收到心跳（主节点故障），自动接管 VIP，成为新主节点；

4. 主节点恢复后，按优先级（`priority`）可能重新抢占 VIP（默认抢占，可关闭）。

#### 6.1.2 什么是会话保持？如何在 Keepalived 中配置？

* **会话保持**：用户多次请求始终路由到同一后端服务器，确保会话信息（如登录状态）不丢失；

* **实现方式**：

  * Keepalived 本身不直接支持，需配合前端负载均衡（如 Nginx 的 `ip_hash`）：

```

upstream app\_servers {

         ip\_hash;  # 按客户端 IP 哈希，实现会话保持

         server 192.168.1.10;

         server 192.168.1.11;

}

```

* 或通过共享会话存储（如 Redis），让所有后端共享会话数据，无需绑定服务器。

### 6.2 高可用架构设计

#### 6.2.1 如何设计一个高可用的 Web 集群架构？

* 架构分层（从客户端到后端）：

1. 客户端层：用户通过域名访问，DNS 解析到负载均衡层 VIP；

2. 负载均衡层：Nginx+Keepalived 主备集群（2 台服务器），负责转发请求和高可用；

3. 应用服务层：多台应用服务器（Tomcat/Node.js），Nginx 负载均衡分担请求；

4. 数据层：数据库主从架构（主写从读），Keepalived 实现数据库高可用；Redis 集群减轻数据库压力；

5. 监控运维：Zabbix 监控各节点，故障自动告警；CI/CD 自动部署。

### 6.3 脑裂问题

#### 6.3.1 脑裂（Split-Brain）问题是什么？如何避免？

* **脑裂**：主备集群因通信故障（如心跳线断），都认为对方故障，同时争抢 VIP，导致客户端请求混乱；

* **避免方法**：

1. 冗余心跳线：多网卡配置多条心跳路径（如内网 + 专线），降低通信中断概率；

2. 权重与抢占控制：主节点设高优先级（`priority 150`），备节点低（`100`）；关闭非必要抢占（`nopreempt`）；

3. 外部检测脚本：备节点脚本检测主节点是否真故障（如公网 ping 主节点），确认后才接管 VIP；

4. STONITH：强制故障节点释放 VIP（如断电、关网络），适合关键场景。

### 6.4 健康检查

#### 6.4.1 健康检查有哪些方式？如何选择？

* **常见方式**：

1. TCP 层检查：检测后端端口是否开放（如 `telnet ``192.168.1.10`` 8080`），简单但无法判断应用状态；

2. HTTP 层检查：请求后端 `/health` 等 URL，判断响应码是否 200，验证应用可用性（Nginx 配置）：

```

upstream app\_servers {

         server 192.168.1.10;

         server 192.168.1.11;

         health\_check interval=5 fails=2 passes=1;  # 5 秒查，2 次失败下线，1 次成功恢复

}

```

1. 自定义脚本检查：脚本执行复杂逻辑（如查数据库连接、磁盘空间），返回 0（正常）/ 非 0（异常），适合业务级检测；

* **选择依据**：

  * 简单服务（TCP 代理）用 TCP 检查；Web 服务用 HTTP 检查；复杂业务用脚本检查；

  * 平衡精度与性能：脚本检查精度高但开销大，合理设检查间隔。
