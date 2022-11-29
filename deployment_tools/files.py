from __future__ import annotations
from dataclasses import dataclass
import os


@dataclass
class Replace:
    old_str: str
    new_str: str
    pattern: str = None

    def replace_in_line(self, line: str) -> str:
        if self.pattern is not None and self.pattern not in line:
            return line
        print(f"\t{self.old_str} => {self.new_str}")
        return line.replace(self.old_str, self.new_str)


@dataclass
class NewLine:
    line: str
    position: int or None = None


class FileTransformer:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._updates: dict[str:str] = dict()
        self._replaces: list[Replace] = []
        self._add_lines: list[NewLine] = []

    def replace_line(self, if_line_contains: str, new_line: str) -> FileTransformer:
        self._updates[if_line_contains] = self._ensure_newline(new_line)
        return self

    def add_line(self, line: str or list[str], row=None):
        lines = [line] if isinstance(line, str) else list(line)[::-1]
        for line in lines:
            self._add_lines.append(NewLine(self._ensure_newline(line), row))
        return self

    def replace_in_line(self, *, pattern: str = None, old_str: str, new_str: str) -> FileTransformer:
        self._replaces.append(
            Replace(old_str=old_str, new_str=new_str, pattern=pattern)
        )
        return self

    @staticmethod
    def _ensure_newline(line: str) -> str:
        if not line.endswith('\n'):
            line += '\n'
        return line

    def _update_line(self, line: str) -> str:
        for pattern, new_line in self._updates.items():
            if pattern in line:
                print(f"{self.path} => setting {new_line}")
                return new_line
        for replace in self._replaces:
            print(f"{self.path} => replacements:")
            return replace.replace_in_line(line)
        return line

    def _get_current_file_lines(self) -> list[str]:
        try:
            with open(self.path, 'r') as existing_file:
                return existing_file.readlines()
        except FileNotFoundError:
            return []

    def apply(self):
        new_lines = [self._update_line(line) for line in self._get_current_file_lines()]
        for line_to_add in self._add_lines:
            if line_to_add.position is None:
                new_lines.append(line_to_add.line)
            else:
                new_lines.insert(line_to_add.position, line_to_add.line)
        with open(self.path, 'w') as new_file:
            new_file.writelines(new_lines)
