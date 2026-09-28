"""读取并递增项目版本号。"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import toml

_VersionSource = tuple[bool, Callable[[], str], Callable[[str], None]]


def _next_version(version: str | None, step: int = 64) -> str:
    """按指定进位值递增三段式版本号。"""
    if step < 2:
        raise ValueError("版本进位值必须大于 1")

    value = version or "0.0.1"
    try:
        parts = [int(part) for part in value.split(".")]
    except ValueError as error:
        raise ValueError(f"版本号必须是三段非负整数: {value}") from error

    if len(parts) != 3 or any(part < 0 for part in parts):
        raise ValueError(f"版本号必须是三段非负整数: {value}")

    encoded = parts[0] * step * step + parts[1] * step + parts[2] + 1
    major, remainder = divmod(encoded, step * step)
    minor, patch = divmod(remainder, step)
    return f"{major}.{minor}.{patch}"


def _legacy_version_source() -> _VersionSource:
    version_path = Path("script/__version__.md")

    def read() -> str:
        return version_path.read_text(encoding="utf-8").strip()

    def write(version: str) -> None:
        version_path.write_text(version, encoding="utf-8")

    return version_path.exists(), read, write


def _version_table(data: dict[str, Any]) -> dict[str, Any]:
    project = data.get("project")
    if isinstance(project, dict) and "version" in project:
        return project

    poetry = data.get("tool", {}).get("poetry")
    if isinstance(poetry, dict) and "version" in poetry:
        return poetry

    raise ValueError("pyproject.toml 未声明 [project].version 或 [tool.poetry].version")


def _pyproject_source() -> _VersionSource:
    pyproject_path = Path("pyproject.toml")

    def read() -> str:
        try:
            return str(_version_table(toml.load(pyproject_path))["version"])
        except (OSError, toml.TomlDecodeError, ValueError) as error:
            raise ValueError(f"无法读取版本文件 {pyproject_path}: {error}") from error

    def write(version: str) -> None:
        try:
            data = toml.load(pyproject_path)
            _version_table(data)["version"] = version
            with pyproject_path.open("w", encoding="utf-8") as file:
                toml.dump(data, file)
        except (OSError, toml.TomlDecodeError, ValueError) as error:
            raise ValueError(f"无法更新版本文件 {pyproject_path}: {error}") from error

    return pyproject_path.exists(), read, write


_VERSION_SOURCES = (_pyproject_source, _legacy_version_source)


def version_read() -> str:
    """读取当前目录中的项目版本号。

    Returns:
        PEP 621、Poetry 或旧版版本文件中的版本号。

    Raises:
        FileNotFoundError: 当前目录不存在受支持的版本源。
        ValueError: pyproject.toml 存在但未声明版本号。
    """
    for source in _VERSION_SOURCES:
        exists, read, _ = source()
        if exists:
            return read()
    raise FileNotFoundError("未找到 pyproject.toml 或 script/__version__.md")


def version_upgrade(
    args: object | None = None, step: int = 64, **kwargs: object
) -> str:
    """读取、递增并写回当前目录中的项目版本号。

    Args:
        args: 命令行参数对象，保留用于 CLI 调用兼容。
        step: 次版本号和修订号的进位值。
        **kwargs: 保留用于调用兼容的额外参数。

    Returns:
        写回后的新版本号。

    Raises:
        FileNotFoundError: 当前目录不存在受支持的版本源。
        ValueError: 版本号或进位值无效。
    """
    for source in _VERSION_SOURCES:
        exists, read, write = source()
        if exists:
            version = _next_version(read(), step=step)
            write(version)
            return version
    raise FileNotFoundError("未找到 pyproject.toml 或 script/__version__.md")
