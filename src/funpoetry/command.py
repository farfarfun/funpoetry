"""funpoetry 命令行入口。"""

import typer

from funpoetry.version import version_upgrade

app = typer.Typer(help="更新项目版本号")


@app.callback()
def main() -> None:
    """更新项目版本号。"""


@app.command("version-upgrade")
def version_upgrade_command() -> None:
    """递增当前项目版本号。"""
    try:
        version_upgrade()
    except (FileNotFoundError, ValueError) as error:
        typer.echo(f"错误: {error}", err=True)
        raise typer.Exit(2) from error


def funpoetry() -> None:
    """解析命令行参数并执行所选子命令。

    Returns:
        None。

    Raises:
        SystemExit: 参数无效或子命令执行失败时以非零状态退出。
    """
    app()
