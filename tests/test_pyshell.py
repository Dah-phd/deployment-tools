from deployment_tools import Command, ShellCommandError
import pytest


def test_run():
    with pytest.raises(ShellCommandError):
        Command(['asd', 'asdadawe']).raise_on_failure()
