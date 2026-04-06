import sqlite3
import json
from urllib import request, error
from datetime import datetime
from pathlib import Path

DB_FILE = "accounts.db"


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT NOT NULL UNIQUE,
            usertoken TEXT NOT NULL,
            status TEXT DEFAULT 'unknown',
            last_checked TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_account(account, usertoken):
    """添加账号"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            "INSERT INTO accounts (account, usertoken, created_at) VALUES (?, ?, ?)",
            (account, usertoken, now)
        )
        conn.commit()
        print("账号 " + account + " 添加成功")
    except sqlite3.IntegrityError:
        print("账号 " + account + " 已存在")
    finally:
        conn.close()


def list_accounts():
    """列出所有账号"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, account, status, last_checked FROM accounts ORDER BY id")
    accounts = cursor.fetchall()
    conn.close()

    if not accounts:
        print("暂无账号")
        return

    print("")
    print("=" * 60)
    print("ID  账号标识                       状态       最后检查时间")
    print("=" * 60)
    for acc in accounts:
        id_, account, status, last_checked = acc
        last_checked = last_checked or "未检查"
        print(str(id_) + "   " + account.ljust(30) + " " + status.ljust(10) + " " + last_checked)
    print("=" * 60)
    print("")


def test_account(account_id=None):
    """测试账号 usertoken 是否过期"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if account_id:
        cursor.execute("SELECT id, account, usertoken FROM accounts WHERE id = ?", (account_id,))
    else:
        cursor.execute("SELECT id, account, usertoken FROM accounts")

    accounts = cursor.fetchall()

    if not accounts:
        print("未找到账号")
        conn.close()
        return

    for acc in accounts:
        id_, account, usertoken = acc
        print("")
        print("正在测试: " + account + "...")

        # 测试 usertoken
        test_urls = [
            "https://chat.deepseek.com/api/v0/users/me",
            "https://chat.deepseek.com/api/v0/user/me",
            "https://chat.deepseek.com/api/v0/profile",
            "https://chat.deepseek.com/",
        ]

        status = "fail"
        message = "所有测试接口均失败"
        last_error = ""

        for url in test_urls:
            try:
                req = request.Request(
                    url=url,
                    method="GET",
                    headers={
                        "Cookie": "usertoken=" + usertoken,
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "application/json, text/html, */*",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                        "Referer": "https://chat.deepseek.com/",
                    }
                )
                with request.urlopen(req, timeout=20) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                    if 200 <= resp.status < 300:
                        status = "ok"
                        message = "测试成功: " + url
                        break
                    last_error = f"{url} -> HTTP {resp.status}"
            except error.HTTPError as e:
                try:
                    body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    body = str(e)
                if e.code in (401, 403):
                    message = "usertoken 已失效"
                    last_error = f"{url} -> HTTPError {e.code} (可能 usertoken 失效)"
                else:
                    last_error = f"{url} -> HTTPError {e.code}: {body[:200]}"
            except error.URLError as e:
                last_error = f"{url} -> URLError: {e.reason}"
            except Exception as e:
                last_error = f"{url} -> UnexpectedError: {e}"

        if status == "fail" and last_error:
            message = last_error

        # 更新数据库
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE accounts SET status = ?, last_checked = ? WHERE id = ?",
            (status, now, id_)
        )
        conn.commit()

        # 显示结果
        if status == "ok":
            print("  成功: " + message)
        else:
            print("  失败: " + message)

    conn.close()
    print("")
    print("测试完成")


def delete_account(account_id):
    """删除账号"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    if cursor.rowcount > 0:
        print("账号 ID " + str(account_id) + " 已删除")
    else:
        print("未找到账号 ID " + str(account_id))
    conn.commit()
    conn.close()


def import_accounts(file_path):
    """从文件批量导入账号"""
    import re

    file_path = Path(file_path)
    if not file_path.exists():
        print("文件不存在: " + str(file_path))
        return

    content = file_path.read_text(encoding='utf-8')

    # 支持多种格式：
    # 1. account:usertoken
    # 2. account|usertoken
    # 3. account usertoken
    # 4. JSON 格式 [{"account": "...", "usertoken": "..."}]（兼容 {"email": "..."}）
    accounts = []

    # 尝试 JSON 格式
    try:
        data = json.loads(content)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'usertoken' in item:
                    account = item.get('account') or item.get('email')
                    if account:
                        accounts.append((account, item['usertoken']))
    except json.JSONDecodeError:
        # 尝试文本格式
        for line in content.strip().split('\n'):
            line = line.strip()
            if not line:
                continue

            match = re.match(r'^([^:|\s]+)[:|\s]+(.+)$', line)
            if match:
                account, usertoken = match.groups()
                accounts.append((account.strip(), usertoken.strip()))

    if not accounts:
        print("未找到有效的账号信息")
        return

    # 批量添加账号
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    success_count = 0
    update_count = 0

    for account, usertoken in accounts:
        # 检查账号是否已存在
        cursor.execute("SELECT id FROM accounts WHERE account = ?", (account,))
        existing = cursor.fetchone()

        if existing:
            # 更新已存在的账号
            cursor.execute(
                "UPDATE accounts SET usertoken = ?, last_checked = NULL WHERE account = ?",
                (usertoken, account)
            )
            update_count += 1
            print("账号 " + account + " 已更新")
        else:
            # 添加新账号
            cursor.execute(
                "INSERT INTO accounts (account, usertoken, created_at) VALUES (?, ?, ?)",
                (account, usertoken, now)
            )
            success_count += 1
            print("账号 " + account + " 添加成功")

    conn.commit()
    conn.close()

    print("")
    print(f"导入完成: 新增 {success_count} 个，更新 {update_count} 个")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek 账号管理器")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 添加账号
    add_parser = subparsers.add_parser("add", help="添加账号")
    add_parser.add_argument("--account", required=True, help="账号标识（邮箱/手机号）")
    add_parser.add_argument("--usertoken", required=True, help="usertoken")

    # 批量导入
    import_parser = subparsers.add_parser("import", help="从文件批量导入账号")
    import_parser.add_argument("--file", required=True, help="包含账号信息的文件路径")

    # 列出账号
    subparsers.add_parser("list", help="列出所有账号")

    # 测试账号
    test_parser = subparsers.add_parser("test", help="测试 usertoken")
    test_parser.add_argument("--id", type=int, help="指定账号ID（不指定则测试所有）")

    # 删除账号
    delete_parser = subparsers.add_parser("delete", help="删除账号")
    delete_parser.add_argument("--id", type=int, required=True, help="账号ID")

    args = parser.parse_args()

    # 确保数据库已初始化
    init_db()

    if args.command == "add":
        add_account(args.account, args.usertoken)
    elif args.command == "import":
        import_accounts(args.file)
    elif args.command == "list":
        list_accounts()
    elif args.command == "test":
        test_account(args.id)
    elif args.command == "delete":
        delete_account(args.id)


if __name__ == "__main__":
    main()
