"""funpoetry 公开 API 与命令行冒烟测试。"""

import subprocess
import sys

import pytest
import toml


def test_import_top_level_package():
    import funpoetry

    assert funpoetry is not None


def test_import_command_module():
    import funpoetry.command

    assert callable(funpoetry.command.funpoetry)


def test_import_version_subpackage():
    from funpoetry import version

    assert callable(version.version_read)
    assert callable(version.version_upgrade)


def test_version_upgrade_bumps_pep621_project(tmp_path, monkeypatch):
    """PEP 621 项目版本应被读取、递增并写回。"""
    from funpoetry.version import version_upgrade

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "dummy"\nversion = "0.0.1"\n')
    monkeypatch.chdir(tmp_path)

    assert version_upgrade() == "0.0.2"
    assert toml.load(pyproject)["project"]["version"] == "0.0.2"


def test_version_upgrade_keeps_poetry_compatibility(tmp_path, monkeypatch):
    """旧版 Poetry 项目仍应能够升级版本。"""
    from funpoetry.version import version_upgrade

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.poetry]\nname = "dummy"\nversion = "1.2.3"\n')
    monkeypatch.chdir(tmp_path)

    assert version_upgrade() == "1.2.4"
    assert toml.load(pyproject)["tool"]["poetry"]["version"] == "1.2.4"


def test_version_read_from_pep621_project(tmp_path, monkeypatch):
    from funpoetry.version import version_read

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "dummy"\nversion = "1.2.3"\n'
    )
    monkeypatch.chdir(tmp_path)

    assert version_read() == "1.2.3"


def test_version_upgrade_falls_back_to_legacy_file(tmp_path, monkeypatch):
    """没有 pyproject.toml 时应回退到旧版版本文件。"""
    from funpoetry.version import version_upgrade

    script_dir = tmp_path / "script"
    script_dir.mkdir()
    version_file = script_dir / "__version__.md"
    version_file.write_text("0.0.1")
    monkeypatch.chdir(tmp_path)

    assert version_upgrade() == "0.0.2"
    assert version_file.read_text() == "0.0.2"


def test_version_upgrade_rejects_missing_source(tmp_path, monkeypatch):
    from funpoetry.version import version_upgrade

    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match="未找到"):
        version_upgrade()


def test_version_upgrade_rejects_invalid_version(tmp_path, monkeypatch):
    from funpoetry.version import version_upgrade

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "dummy"\nversion = "invalid"\n'
    )
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="三段非负整数"):
        version_upgrade()


def test_cli_help_exits_cleanly(monkeypatch):
    from funpoetry.command import funpoetry

    monkeypatch.setattr(sys, "argv", ["funpoetry", "--help"])

    with pytest.raises(SystemExit) as error:
        funpoetry()

    assert error.value.code == 0


def test_cli_requires_subcommand(monkeypatch):
    from funpoetry.command import funpoetry

    monkeypatch.setattr(sys, "argv", ["funpoetry"])

    with pytest.raises(SystemExit) as error:
        funpoetry()

    assert error.value.code == 2


def test_cli_failure_uses_nonzero_exit(tmp_path, monkeypatch, capsys):
    from funpoetry.command import funpoetry

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["funpoetry", "version-upgrade"])

    with pytest.raises(SystemExit) as error:
        funpoetry()

    assert error.value.code == 2
    assert "未找到" in capsys.readouterr().err


def test_console_script_help_via_subprocess():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from funpoetry.command import funpoetry; "
            "import sys; sys.argv=['funpoetry','--help']; funpoetry()",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_cli_version_upgrade_subcommand(tmp_path, monkeypatch):
    from funpoetry.command import funpoetry

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "dummy"\nversion = "0.0.1"\n')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["funpoetry", "version-upgrade"])

    funpoetry()

    assert toml.load(pyproject)["project"]["version"] == "0.0.2"
