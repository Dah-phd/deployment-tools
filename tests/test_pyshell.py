from deployment_tools.pyshell import Command, ShellCommandError
import pytest
from sys import platform


def run_command_based_on_platform(unix: list[str], win: list[str]) -> Command:
    return Command(unix) if platform != 'win32' else Command(win)


def test_ls():
    cmd = run_command_based_on_platform(['ls'], ['dir'])
    assert cmd.output != [''] and cmd.error == ['']


def test_generic_fail():
    with pytest.raises(ShellCommandError):
        Command(['asd', 'asdadawe']).raise_on_failure()


def test_non_success_raise():
    with pytest.raises(ShellCommandError):
        cmd = run_command_based_on_platform(['ls'], ['dir'])
        cmd.set_success('non_existing_file').raise_on_failure()


def test_succss():
    cmd = run_command_based_on_platform(['ls'], ['dir']).set_success('deployment_tools')
    assert cmd.is_success() and not cmd.is_failure()


def test_not_success():
    cmd = run_command_based_on_platform(['ls'], ['dir']).set_success('non_existing_file')
    assert not cmd.is_success()


def test_err_not_failure():
    cmd = Command(['asdasf']).set_failure('d;lfjasl;pkfjasol;f')
    assert not cmd.is_failure()
