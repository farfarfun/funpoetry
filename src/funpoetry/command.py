"""funpoetry 命令行入口。"""

import argparse

from funpoetry.version import version_upgrade


def funpoetry() -> None:
    """解析命令行参数并执行所选子命令。

    Returns:
        None。

    Raises:
        SystemExit: 参数无效或子命令执行失败时以非零状态退出。
    """
    parser = argparse.ArgumentParser(prog="funpoetry", description="更新项目版本号")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 添加子命令
    upgrade_parser = subparsers.add_parser("version-upgrade", help="递增当前项目版本号")
    upgrade_parser.set_defaults(func=version_upgrade)

    args = parser.parse_args()
    try:
        args.func(args)
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))
