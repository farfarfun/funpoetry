"""Lightweight smoke tests for funpoetry.

funpoetry is a tiny CLI helper that bumps the version number stored either
in ``./pyproject.toml`` (``[tool.poetry].version``) or in a legacy
``./script/__version__.md`` file. It does not shell out to ``poetry``,
``git`` or ``twine`` and does not perform any network I/O - all it does is
read/write a version string from/to a file in the current working
directory. These tests therefore run the real functions but always do so
inside an isolated ``tmp_path`` (via ``monkeypatch.chdir``) so nothing in
the real checkout or environment is ever touched.
"""

import subprocess
import sys

import pytest


def test_import_top_level_package():
    import funpoetry  # noqa: F401


def test_import_command_module():
    import funpoetry.command  # noqa: F401

    assert hasattr(funpoetry.command, "funpoetry")
    assert callable(funpoetry.command.funpoetry)


def test_import_version_subpackage():
    from funpoetry import version

    assert hasattr(version, "version_read")
    assert hasattr(version, "version_upgrade")
    assert callable(version.version_read)
    assert callable(version.version_upgrade)


def test_import_upgrade_module():
    from funpoetry.version import upgrade  # noqa: F401

    assert hasattr(upgrade, "method_list")
    assert len(upgrade.method_list) == 2


def test_version_upgrade_bumps_pyproject_toml(tmp_path, monkeypatch):
    """version_upgrade() should read the version from ./pyproject.toml,
    bump it, and write the new value back - without touching any real
    project file, since we chdir into a throwaway tmp_path first."""
    from funpoetry.version import version_upgrade

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.poetry]\nname = "dummy"\nversion = "0.0.1"\n'
    )
    monkeypatch.chdir(tmp_path)

    new_version = version_upgrade()

    assert new_version != "0.0.1"
    # the on-disk file must reflect the bump
    import toml

    data = toml.load(pyproject)
    assert data["tool"]["poetry"]["version"] == new_version


def test_version_read_from_pyproject_toml(tmp_path, monkeypatch):
    from funpoetry.version import version_read

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.poetry]\nname = "dummy"\nversion = "1.2.3"\n'
    )
    monkeypatch.chdir(tmp_path)

    assert version_read() == "1.2.3"


def test_version_upgrade_fallback_to_legacy_version_file(tmp_path, monkeypatch):
    """When there is no pyproject.toml, funpoetry falls back to the legacy
    ./script/__version__.md file (method1)."""
    from funpoetry.version import version_upgrade

    script_dir = tmp_path / "script"
    script_dir.mkdir()
    version_file = script_dir / "__version__.md"
    version_file.write_text("0.0.1")

    monkeypatch.chdir(tmp_path)

    new_version = version_upgrade()

    assert new_version != "0.0.1"
    assert version_file.read_text() == new_version


def test_version_upgrade_no_version_source_prints_message(tmp_path, monkeypatch, capsys):
    """If neither pyproject.toml nor the legacy version file exists,
    version_upgrade() should not raise - it just reports it isn't
    supported."""
    from funpoetry.version import version_upgrade

    monkeypatch.chdir(tmp_path)

    result = version_upgrade()

    assert result is None
    captured = capsys.readouterr()
    assert "not support" in captured.out


def test_cli_help_exits_cleanly(monkeypatch):
    """Invoke the argparse-based CLI entry point with --help and make sure
    it exits with status 0, without running any real subcommand."""
    from funpoetry.command import funpoetry

    monkeypatch.setattr(sys, "argv", ["funpoetry", "--help"])

    with pytest.raises(SystemExit) as exc_info:
        funpoetry()

    assert exc_info.value.code == 0


def test_cli_console_script_help_via_subprocess():
    """The installed console_script entry point (declared in
    [tool.poetry.scripts]) should be runnable and exit cleanly on --help."""
    result = subprocess.run(
        [sys.executable, "-c", "from funpoetry.command import funpoetry; import sys; sys.argv=['funpoetry','--help']; funpoetry()"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_cli_version_upgrade_subcommand(tmp_path, monkeypatch):
    """Smoke-test the 'version-upgrade' subcommand end-to-end. This only
    touches files inside an isolated tmp_path, never the real repo, and
    never shells out to git/poetry/twine or the network."""
    from funpoetry.command import funpoetry

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.poetry]\nname = "dummy"\nversion = "0.0.1"\n'
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["funpoetry", "version-upgrade"])

    funpoetry()

    import toml

    data = toml.load(pyproject)
    assert data["tool"]["poetry"]["version"] != "0.0.1"
