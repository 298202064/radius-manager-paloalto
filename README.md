# RADIUS 认证管理系统

这是一套基于 FreeRADIUS + FastAPI + Vue 3 的 RADIUS 认证管理系统，支持用户管理（可以手工创建也可以从企业AD做导入）、支持OTP 双因素认证、认证日志审计和自助服务，通过 Docker Compose 一键部署。完全适配Palo Alto Networks的防火墙部署GlobalProtect集成，也可以部署在企业数据中心和Prisma Access的Service Connection对接后为GlobalProtect用户接入提供MFA身份验证。

## 系统架构

```
                    ┌─────────────┐
                    │   Nginx     │  (端口 8081)
                    │   Frontend  │
                    └──────┬──────┘
                           │ /api/
                    ┌──────▼──────┐
                    │   FastAPI   │  (端口 8000, 仅内部)
                    │   Backend   │
                    └──┬──────┬───┘
                       │      │
              ┌────────▼┐  ┌──▼────────┐
              │PostgreSQL│  │   Redis   │
              │  (5432)  │  │  (6379)   │
              └──┬───────┘  └───────────┘
                 │ rlm_sql / rlm_rest
          ┌──────▼───────┐
          │  FreeRADIUS  │  (端口 1812/1813 UDP)
          │              │
          └──────────────┘
```

## 核心功能

| 功能 | 说明 |
|------|------|
| **用户管理** | 创建/编辑/删除用户，启用/禁用账户，设置角色 |
| **RADIUS 认证** | 标准 PAP 认证，支持 FreeRADIUS 接入 |
| **OTP 双因素认证** | TOTP 协议，两步验证（Access-Challenge），兼容 Google/Microsoft Authenticator |
| **认证日志** | 记录所有认证成功/失败记录，支持多维筛选 |
| **在线用户** | 实时查看 GlobalProtect VPN 在线用户（通过 PAN-OS API） |
| **NAS 管理** | 管理 RADIUS 客户端（NAS）配置 |
| **只读网关管理** | 管理 PAN-OS 防火墙只读网关，用于获取 VPN 在线用户 |
| **LDAP 集成** | 配置 AD/LDAP 服务器，搜索并导入用户到本地数据库 |
| **自助服务** | 用户自助修改密码、绑定/解绑 OTP 设备 |

## 环境要求

- Docker Engine >= 20.10
- Docker Compose >= 2.0
- 最低配置: 2核 CPU / 4GB 内存 / 20GB 磁盘

## 快速部署

> 详细部署手册请参考 [docs/deployment.md](docs/deployment.md)。

### 1. 拷贝项目到目标主机

将整个 `radius-manager` 目录拷贝到新主机任意位置，然后进入目录：

```bash
cd /path/to/radius-manager
```

如果需要从 Git 仓库拉取：

```bash
git clone <项目地址>
cd radius-manager
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 修改 .env 中的配置，特别是 SECRET_KEY 和 ENCRYPTION_KEY
```

生成加密密钥：

```bash
# 生成 Fernet 加密密钥（用于加密 OTP 密钥和 NAS 密钥）
docker run --rm python:3.12-slim python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. 启动服务

```bash
docker compose up -d
```

首次启动会自动创建数据库表结构并初始化默认管理员账户。

### 4. 访问系统

- Web 管理界面: http://localhost:8081
- 默认管理员: `admin` / `admin123`

> **重要**: 首次登录后请立即修改默认密码！

## 服务说明

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| PostgreSQL | radius-postgres | 5432 (宿主机: 5433) | 数据库 |
| Redis | radius-redis | 6379 | 缓存 |
| Backend | radius-backend | 8000 | FastAPI 后端 API |
| FreeRADIUS | radius-freeradius | 1812/1813 UDP | RADIUS 认证/计费服务器 |
| Frontend | radius-frontend | 8081 | Nginx + Vue 3 前端 |

## 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DB_NAME` | radius | 数据库名称 |
| `DB_USER` | radius | 数据库用户 |
| `DB_PASSWORD` | radiuspass | 数据库密码 |
| `SECRET_KEY` | (必填) | JWT 签名密钥，生产环境必须修改 |
| `ENCRYPTION_KEY` | (必填) | Fernet 加密密钥，用于加密 OTP 密钥和 NAS 密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | JWT access token 过期时间（分钟） |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | JWT refresh token 过期时间（天） |
| `CORS_ORIGINS` | http://localhost:8081 | CORS 允许的源 |

## 管理指南

### 用户管理

1. 登录后进入 **用户管理** 页面
2. 点击 **新建用户**，填写用户名、密码、邮箱等信息
3. 用户可以设置为 **管理员** 或 **普通用户** 角色
4. 管理员可编辑、删除用户，重置密码
5. 可以查看用户的 OTP 绑定状态并强制解绑

### NAS 客户端配置

1. 进入 **NAS客户端** 页面
2. 点击 **新建客户端**，填写 NAS 设备信息（名称、IP地址、共享密钥、设备类型等）
3. 保存后系统 **自动同步** 配置到 FreeRADIUS 并重载服务，无需手动操作
4. 新建、编辑或删除客户端时，系统会自动更新 `clients.conf` 文件并发送 HUP 信号重载 FreeRADIUS
5. 如需手动触发同步，点击 **同步配置** 按钮即可

### 只读网关管理

用于配置 PAN-OS 防火墙只读网关，系统通过 PAN-OS API 自动获取 GlobalProtect VPN 在线用户。

1. 进入 **只读网关** 页面
2. 点击 **新建网关**，填写网关名称、管理 IP 地址、只读用户名和密码
3. 添加后点击 **测试连接** 验证是否能成功获取在线用户信息
4. 启用网关后，仪表盘和在线用户页面将自动显示该网关的在线用户
5. 支持添加多个网关，系统会汇总所有网关的在线用户数据

> **注意**: 使用的 PAN-OS 账号只需具备只读权限，系统通过 API 密钥方式认证，不会存储明文密码（使用 Fernet 加密）。

### LDAP 集成

用于配置 Active Directory LDAP 服务器，将 AD 用户导入到本系统的用户数据库，无需管理员逐个手动创建用户。

1. 进入 **只读LDAP** 页面
2. 点击 **新增服务器**，填写 AD 服务器信息（主机地址、端口、Base DN、Bind DN、Bind 密码）
3. 点击 **测试连接** 验证 LDAP 配置是否正确
4. 点击 **导入用户**，系统将从 AD 搜索用户并显示预览列表
5. 勾选需要导入的用户，点击 **导入选中用户**
6. 导入的用户将自动获得随机初始密码，出现在 **用户管理** 列表中
7. 管理员可为导入的用户启用 OTP，用户可在 **自助服务** 页面修改密码

> **注意**: AD 只作为用户身份来源，RADIUS 认证仍使用本系统存储的密码 + OTP，不依赖 AD 在线验证。已存在的用户名将被跳过，不会覆盖。

### 认证日志审计

1. 进入 **认证日志** 页面
2. 支持按用户名、时间范围、认证结果筛选
3. 日志包含呼叫方/被叫方信息，便于问题排查

### 查看在线用户

1. 进入 **在线用户** 页面
2. 实时显示当前在线用户列表
3. 可查看用户的上下行流量、上线时长等信息

## OTP 配置指南

### 用户自助绑定 OTP

1. 登录后点击左侧 **自助服务 → OTP管理**
2. 点击 **检查状态** 确认当前 OTP 状态
3. 点击 **获取二维码**，页面会生成一个二维码
4. 使用手机上的 Google Authenticator 或 Authy 扫描二维码
5. 输入 App 中显示的 6 位验证码，点击 **确认绑定**

### OTP 认证方式

启用 OTP 后，RADIUS 认证采用 **两步验证**（Access-Challenge）流程：

1. **第一步 — 密码验证**: 在 VPN 客户端输入用户名和静态密码提交
2. **第二步 — OTP 验证**: FreeRADIUS 验证密码通过后，向客户端返回 Access-Challenge
3. 客户端弹出输入框显示提示信息（如 "Enter 6-digit verification code"）
4. 输入手机上 Authenticator App（Google/Microsoft 等）显示的 6 位验证码
5. FreeRADIUS 通过 rlm_rest 调用后端 API 完成 OTP 校验，认证通过

### 管理员解绑用户 OTP

1. 进入 **用户管理** 页面
2. 点击用户的 **OTP** 按钮查看 OTP 状态
3. 点击 **解除绑定** 按钮即可强制解绑

## FreeRADIUS 配置参考

### 认证流程

1. NAS 发送 Access-Request 到 FreeRADIUS (UDP 1812)
2. FreeRADIUS `authorize` 阶段:
   - `rlm_sql` 从 `radcheck` 表加载用户属性
   - 检查用户是否启用 OTP（查询 `otp_devices` 表）
   - 非 OTP 用户: Auth-Type = PAP
   - OTP 用户第一次请求（无 State）: Auth-Type = PAP（验证密码）
   - OTP 用户挑战响应（有 State）: Auth-Type = rest_otp
3. FreeRADIUS `authenticate` 阶段:
   - PAP: rlm_sql 比较 Cleartext-Password（非 OTP 用户）
   - OTP 用户密码验证通过后 → 发送 **Access-Challenge**（含 Reply-Message 和 State）
   - rest_otp: rlm_rest 调用 FastAPI 验证 OTP 码（OTP 用户第二步）
4. 结果记录到 `radpostauth` 表

### 数据库表

| 表名 | 说明 |
|------|------|
| `users` | 系统用户（管理员/普通用户） |
| `radcheck` | RADIUS 认证检查属性（密码） |
| `radreply` | RADIUS 认证回复属性（IP 分配等） |
| `radacct` | RADIUS 计费/在线记录 |
| `radpostauth` | RADIUS 认证日志 |
| `otp_devices` | OTP 设备绑定（加密存储 TOTP 密钥） |
| `nas_clients` | NAS 客户端配置（加密存储共享密钥） |
| `readonly_gateways` | 只读网关配置（加密存储 PAN-OS 密码） |
| `ldap_configs` | LDAP 服务器配置（加密存储 Bind 密码） |
| `refresh_tokens` | JWT 刷新令牌 |

### NAS 配置

FreeRADIUS 的 `clients.conf` 通过 Web 界面自动管理。配置格式：

```conf
client <名称> {
    ipaddr = <IP地址/网段>
    secret = <共享密钥>
    nas_type = <设备类型>
}
```

在 Web 界面中新建、编辑或删除 NAS 客户端后，系统会自动将配置写入 FreeRADIUS 的 `clients.conf` 并通过 HUP 信号重载服务，无需手动复制文件或重启容器。

如需手动触发同步，可在 **NAS客户端管理** 页面点击 **同步配置** 按钮，系统将重新生成完整的 `clients.conf` 并重载 FreeRADIUS。

## 备份与恢复

### 备份数据库

```bash
docker exec radius-postgres pg_dump -U radius radius > backup_$(date +%Y%m%d).sql
```

### 恢复数据库

```bash
cat backup_20260101.sql | docker exec -i radius-postgres psql -U radius radius
```

## 安全注意事项

1. **修改默认密码**: 首次登录后立即修改 `admin` 密码
2. **配置加密密钥**: 设置强随机 `SECRET_KEY` 和 `ENCRYPTION_KEY`
3. **网络隔离**: Docker 内部网络 `internal` 不对外暴露，只有必要端口映射到宿主机
4. **TLS/SSL**: 生产环境建议在 Nginx 配置 HTTPS
5. **定期备份**: 定期备份 PostgreSQL 数据库
6. **密码策略**: 建议启用强密码策略（已在 API 层做基本校验）
7. **日志审计**: 定期检查认证日志，发现异常及时处理

## 故障排查

### 验证 RADIUS 服务

```bash
# 测试 PAP 认证（非 OTP 用户）
docker run --rm --network host --entrypoint sh radius-manager-freeradius:latest \
  -c "radtest testuser test123 127.0.0.1 1812 testing123"

# 测试 OTP 两步认证（需先绑定 OTP）
# 第一步: 密码验证 — 返回 Access-Challenge
docker run --rm --network host --entrypoint sh radius-manager-freeradius:latest \
  -c "radtest testuser test123 127.0.0.1 1812 testing123"

# 第二步: OTP 验证（$code 为当前 TOTP, $state 为上一步返回的 State）
# echo 'User-Name = "testuser", User-Password = "'$code'", State = '$state \
#   | docker run --rm -i --network host --entrypoint sh radius-manager-freeradius:latest \
#   -c "radclient 127.0.0.1:1812 auth testing123"

# 测试计费
echo 'User-Name = "testuser", Acct-Session-Id = "test-001", Acct-Status-Type = Start, NAS-IP-Address = 10.0.0.1' \
  | docker run --rm -i --network host --entrypoint sh radius-manager-freeradius:latest \
  -c "radclient -x 127.0.0.1:1813 acct testing123"
```

### FreeRADIUS 无法启动

```bash
# 查看日志
docker logs radius-freeradius

# 检查配置
docker exec radius-freeradius radiusd -C
```

### 认证失败

1. 检查 `radcheck` 表中用户是否存在且密码正确
2. 检查认证日志获取详细错误信息
3. 确认 NAS 客户端 IP 和密钥配置正确
4. 对于 OTP 用户，确认 TOTP 验证码在有效期内

### 数据库连接问题

```bash
# 检查数据库状态
docker exec radius-postgres pg_isready -U radius

# 查看连接
docker exec radius-postgres psql -U radius -c "\conninfo"
```

### Web UI 无法访问

```bash
# 检查所有服务状态
docker-compose ps

# 查看后端日志
docker logs radius-backend

# 查看前端日志
docker logs radius-frontend
```

## 开发指南

### 目录结构

```
radius-manager/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── core/               # 配置、数据库、安全、依赖
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic 数据模式
│   │   ├── api/v1/             # API 端点
│   │   ├── services/           # 业务逻辑层
│   │   └── utils/              # 工具函数
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 客户端
│   │   ├── router/             # 路由配置
│   │   ├── store/              # 状态管理
│   │   ├── components/         # 公共组件
│   │   └── views/              # 页面组件
│   └── Dockerfile
├── config/
│   ├── freeradius/             # FreeRADIUS 配置
│   ├── nginx/                  # Nginx 配置
│   └── init.sql                # 数据库初始化
├── scripts/                    # 辅助脚本
└── docker-compose.yml          # 容器编排
```

### 本地开发

```bash
# 启动数据库依赖
docker-compose up -d postgres redis

# 启动后端（热重载）
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 启动前端（热重载）
cd frontend
npm install
npm run dev
```

## API 文档

启动后端后，API 文档地址（需通过 Nginx 访问）：

- Swagger UI: http://localhost:8081/docs
- ReDoc: http://localhost:8081/redoc

### 主要接口

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | /api/v1/auth/login | 无 | 登录获取令牌 |
| POST | /api/v1/auth/refresh | 无 | 刷新令牌 |
| POST | /api/v1/auth/logout | Bearer | 登出 |
| GET | /api/v1/users | Admin | 用户列表 |
| POST | /api/v1/users | Admin | 创建用户 |
| PUT | /api/v1/users/{id} | Admin | 编辑用户 |
| DELETE | /api/v1/users/{id} | Admin | 删除用户 |
| GET | /api/v1/nas-clients | Admin | NAS 客户端列表 |
| POST | /api/v1/nas-clients | Admin | 创建 NAS 客户端 |
| GET | /api/v1/gateways | Admin | 只读网关列表 |
| POST | /api/v1/gateways | Admin | 创建只读网关 |
| PUT | /api/v1/gateways/{id} | Admin | 编辑只读网关 |
| DELETE | /api/v1/gateways/{id} | Admin | 删除只读网关 |
| POST | /api/v1/gateways/{id}/test | Admin | 测试网关连接 |
| GET | /api/v1/gateways/online-users | Admin | 获取在线用户 |
| GET | /api/v1/ldap/configs | Admin | LDAP 配置列表 |
| POST | /api/v1/ldap/configs | Admin | 创建 LDAP 配置 |
| PUT | /api/v1/ldap/configs/{id} | Admin | 编辑 LDAP 配置 |
| DELETE | /api/v1/ldap/configs/{id} | Admin | 删除 LDAP 配置 |
| POST | /api/v1/ldap/configs/{id}/test | Admin | 测试 LDAP 连接 |
| POST | /api/v1/ldap/configs/{id}/search | Admin | 搜索 AD 用户 |
| POST | /api/v1/ldap/configs/{id}/import | Admin | 导入 AD 用户 |
| GET | /api/v1/logs/auth | Admin | 认证日志 |
| GET | /api/v1/logs/online | Admin | 在线用户 |
| GET | /api/v1/dashboard/stats | Admin | 仪表盘统计 |
| PUT | /api/v1/self/password | Bearer | 修改密码 |
| GET | /api/v1/self/otp/qrcode | Bearer | 获取 OTP 二维码 |
| POST | /api/v1/self/otp/bind | Bearer | 绑定 OTP 设备 |
| DELETE | /api/v1/self/otp | Bearer | 解绑 OTP 设备 |
| POST | /api/v1/radius/authenticate | 内部 | FreeRADIUS OTP 验证 |
| POST | /api/v1/radius/accounting | 内部 | FreeRADIUS 计费转发 |

## 许可证

MIT
