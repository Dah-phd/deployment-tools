from __future__ import annotations
import subprocess
from sys import platform as PLATFORM


class ShellCommandError(Exception):
    pass


class Command:
    """
    Runs command and check output for success, can be used to raise exception in case the command failes.
    Example:
    Command(["python3", "-m", "unittest", "test_file.py"]).set_failure("FAILED (failures=").raise_on_failure()
    If the tests run by the command fail exception with information will be raised, otherwise the code will proceed with execution.
    """

    def __init__(self, args: list[str], verbose: bool = True) -> None:
        self.args = args
        self._process = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        self._failure_cond = None
        self._success_cond = None
        self.output = self._normalize_output(self._process.stdout)
        self.error = self._normalize_output(self._process.stderr)
        verbose and self.log_output()
        self.log_errors()

    def log_output(self):
        for line in self.output:
            print(f'\t{line}')

    def log_errors(self):
        """
        logs infromation stored in stderr
        """
        if self.error != ['']:
            print(f"STDERR logs on {' '.join(self.args)}:")

            for err in self.error:
                print(err)
        else:
            print("Status: OK")

    @staticmethod
    def _normalize_output(result: bytes) -> str:
        return str(result)[2:-1].split("\\n")

    def set_success(self, expect_line: str, on_line: int = None) -> Command:
        """
        Set success condition, where:
        :param: expected_line[str] - specifies information expected in stdout of the command (checks if param is present in any line of the output);
        :param: on_line[int] = None - if specified it will look for the output at a specific line;
        """
        self._success_cond = expect_line if on_line is None else (on_line, expect_line)
        return self

    def set_failure(self, expect_line: str, on_line: int = None) -> Command:
        """
        Set success condition, where:
        :param: expected_line[str] - specifies information expected in stderr of the command (checks if param is present in any line of the output);
        :param: on_line[int] = None - if specified it will look for the err at a specific line;
        """
        self._failure_cond = expect_line if on_line is None else (on_line, expect_line)
        return self

    def is_success(self) -> bool:
        """
        Check success condition;
        """
        if self._success_cond is None:
            return True
        if isinstance(self._success_cond, tuple):
            return self._success_cond[1] in self.output[self._success_cond[0]]
        if isinstance(self._success_cond, str):
            for cmd_line in self.output:
                if self._success_cond in cmd_line:
                    return True
        return False

    def is_failure(self) -> bool:
        """
        Check failure condition;
        """
        if self._failure_cond is None and self.error != ['']:
            return True
        if isinstance(self._failure_cond, tuple):
            return self._failure_cond[1] in self.error[self._failure_cond[0]]
        if isinstance(self._failure_cond, str):
            for cmd_line in self.error:
                if self._failure_cond in cmd_line:
                    return True
        return False

    def raise_on_failure(self):
        """
        raises exception if Command is not success or is failure;
        """
        if self.is_success() and not self.is_failure():
            return
        print("SCRIPT INTERRUPTED!!!")
        self._failure_cond and print(f'\nFound in errors: "{self._failure_cond}"\n')
        self._success_cond and print(f'\nNot found in outputs: "{self._success_cond}"\n')
        raise ShellCommandError(
            f"on command: {' '. join(self.args)}"
        )
