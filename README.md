# DeepSeek Account Manager

一个用于本地管理 DeepSeek `usertoken` 的 Python 工具。  
支持命令行（CLI）和交互式菜单两种使用方式，数据存储在本地 SQLite 数据库中。

---

## 功能特性

- 初始化本地 SQLite 数据库（`accounts.db`）
- 添加单个账号（`account + usertoken`）
- 批量导入账号（文本 / JSON）
- 列出全部账号状态
- 测试账号 token 是否可用（单个或全部）
- 删除指定账号

---

## 项目结构

```text
.
├─ account_manager.py   # 核心逻辑 + CLI 入口
├─ interactive.py       # 交互式菜单入口
├─ accounts.db          # SQLite 数据库（运行后生成）
└─ usertoken.txt        # 可选：批量导入示例文件
```

---

## 环境要求

- Python 3.8+
- 仅使用 Python 标准库（无需额外安装依赖）

---

## 快速开始

### 1) 交互式模式

```bash
python interactive.py
```

菜单操作包括：

1. 添加账号
2. 批量导入账号
3. 列出所有账号
4. 测试账号
5. 删除账号

---

### 2) 命令行模式（CLI）

```bash
python account_manager.py <command> [options]
```

#### 添加账号

```bash
python account_manager.py add --account your_account --usertoken your_token
```

示例：

```bash
python account_manager.py add --account 13800138000 --usertoken xxxxxx
python account_manager.py add --account your_email@example.com --usertoken xxxxxx
```

#### 批量导入

```bash
python account_manager.py import --file ./usertoken.txt
```

#### 列出账号

```bash
python account_manager.py list
```

#### 测试全部账号

```bash
python account_manager.py test
```

#### 测试指定账号

```bash
python account_manager.py test --id 1
```

#### 删除账号

```bash
python account_manager.py delete --id 1
```

---

## 导入格式说明

### 文本格式（每行一条）

支持以下分隔方式：

1. `account:usertoken`
2. `account|usertoken`
3. `account usertoken`

示例：

```text
13800138000:token_xxx
user@example.com|token_yyy
my_account token_zzz
```

### JSON 格式

推荐格式：

```json
[
  {"account": "13800138000", "usertoken": "token_xxx"},
  {"account": "user@example.com", "usertoken": "token_yyy"}
]
```

兼容旧格式（历史数据）：

```json
[
  {"email": "a@example.com", "usertoken": "token_xxx"},
  {"email": "b@example.com", "usertoken": "token_yyy"}
]
```

---

## 数据库结构

数据库文件：`accounts.db`  
数据表：`accounts`

字段说明：

- `id`：主键，自增
- `account`：账号标识（唯一）
- `usertoken`：登录 token
- `status`：账号状态（`unknown` / `ok` / `fail`）
- `last_checked`：最后检测时间
- `created_at`：创建时间

---

## Token 检测逻辑（源码实现）

程序会携带 `Cookie: usertoken=<token>` 依次请求以下地址，任意成功即判定可用：

- `https://chat.deepseek.com/api/v0/users/me`
- `https://chat.deepseek.com/api/v0/user/me`
- `https://chat.deepseek.com/api/v0/profile`
- `https://chat.deepseek.com/`

检测结果会写回数据库中的 `status` 与 `last_checked` 字段。

---

## 免责声明

本项目仅用于学习与本地账号管理，请遵守相关平台服务条款与法律法规，不用于任何未授权用途。