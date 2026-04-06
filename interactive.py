#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek 账号管理器 - 交互式界面
"""

from account_manager import (
    init_db,
    add_account,
    list_accounts,
    test_account,
    delete_account,
    import_accounts
)


def print_menu():
    """打印菜单"""
    print("")
    print("=" * 50)
    print("       DeepSeek 账号管理器")
    print("=" * 50)
    print("1. 添加账号")
    print("2. 批量导入账号")
    print("3. 列出所有账号")
    print("4. 测试账号")
    print("5. 删除账号")
    print("0. 退出")
    print("=" * 50)
    print("")


def add_account_interactive():
    """交互式添加账号"""
    print("\n--- 添加账号 ---")
    account = input("请输入账号（邮箱/手机号）: ").strip()
    if not account:
        print("账号不能为空！")
        return

    usertoken = input("请输入 usertoken: ").strip()
    if not usertoken:
        print("usertoken 不能为空！")
        return

    add_account(account, usertoken)


def import_accounts_interactive():
    """交互式批量导入账号"""
    print("\n--- 批量导入账号 ---")
    print("支持的文件格式:")
    print("  1. account:usertoken")
    print("  2. account|usertoken")
    print("  3. account usertoken")
    print("  4. JSON 格式（支持 account 字段，也兼容 email 字段）")
    print("")

    file_path = input("请输入文件路径: ").strip()
    if not file_path:
        print("文件路径不能为空！")
        return

    import_accounts(file_path)


def list_accounts_interactive():
    """交互式列出账号"""
    print("\n--- 账号列表 ---")
    list_accounts()


def test_account_interactive():
    """交互式测试账号"""
    print("\n--- 测试账号 ---")
    choice = input("测试所有账号还是指定账号？(all/id): ").strip().lower()

    if choice == "all" or choice == "":
        test_account()
    elif choice == "id":
        try:
            account_id = int(input("请输入账号ID: ").strip())
            test_account(account_id)
        except ValueError:
            print("无效的ID！")
    else:
        print("无效的选择！")


def delete_account_interactive():
    """交互式删除账号"""
    print("\n--- 删除账号 ---")

    # 先显示账号列表
    list_accounts()

    try:
        account_id = int(input("请输入要删除的账号ID: ").strip())
        confirm = input(f"确认删除账号 ID {account_id}？(y/n): ").strip().lower()
        if confirm == "y":
            delete_account(account_id)
        else:
            print("已取消删除")
    except ValueError:
        print("无效的ID！")


def main():
    """主函数"""
    # 确保数据库已初始化
    init_db()

    while True:
        print_menu()
        choice = input("请选择操作 (0-5): ").strip()

        if choice == "1":
            add_account_interactive()
        elif choice == "2":
            import_accounts_interactive()
        elif choice == "3":
            list_accounts_interactive()
        elif choice == "4":
            test_account_interactive()
        elif choice == "5":
            delete_account_interactive()
        elif choice == "0":
            print("\n感谢使用，再见！")
            break
        else:
            print("\n无效的选择，请重新输入！")

        input("\n按回车键继续...")


if __name__ == "__main__":
    main()
