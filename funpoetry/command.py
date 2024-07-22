"""
打包的工具类
"""

import argparse

from funpoetry.version import version_upgrade


def funpoetry():
    parser = argparse.ArgumentParser(prog="PROG")
    subparsers = parser.add_subparsers(help="sub-command help")

    # 添加子命令
    build_parser = subparsers.add_parser("version-upgrade", help="build package")
    build_parser.set_defaults(func=version_upgrade)  # 设置默认函数

    args = parser.parse_args()
    args.func(args)
