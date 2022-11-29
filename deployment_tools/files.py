from __future__ import annotations
from dataclasses import dataclass


@dataclass
class _Replace:
    new_str: str = ''
    old_str: str = ''
    new_line: set = None
    pattern: str = None

    def make_updates(self, line: str) -> str:
        if self.pattern is not None:
            if self.pattern not in line:
                return line
            if self.new_line is not None:
                print(f"\t{line} => {self.new_line}")
                return self.new_line
        print(f"\t{self.old_str} => {self.new_str}")
        return line.replace(self.old_str, self.new_str)


@dataclass
class _NewLine:
    line: str
    position: int or None = None

    def self_insert_into(self, lines_list: list[str]) -> list[str]:
        if self.position is None:
            lines_list.append(self.line)
        else:
            lines_list.insert(self.position, self.line)
        return lines_list


class FileTransformer:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._replaces: list[_Replace] = []
        self._lines_to_add: list[_NewLine] = []

    def replace_line(self, pattern: str, new_line: str) -> FileTransformer:
        self._replaces.append(_Replace(new_line=new_line, pattern=pattern))
        return self

    def replace_in_line(self, *, pattern: str = None, old_str: str, new_str: str) -> FileTransformer:
        self._replaces.append(_Replace(old_str=old_str, new_str=new_str, pattern=pattern))
        return self

    def add_line(self, line: str or list[str], row=None):
        lines = [line] if isinstance(line, str) else list(line)[::-1]
        for line in lines:
            self._lines_to_add.append(_NewLine(self._ensure_newline(line), row))
        return self

    @staticmethod
    def _ensure_newline(line: str) -> str:
        if not line.endswith('\n'):
            line += '\n'
        return line

    def _update_line(self, line: str) -> str:
        for line_replace in self._replaces:
            line = line_replace.make_updates(line)
        return line

    def _get_current_file_lines(self) -> list[str]:
        try:
            with open(self.path, 'r') as existing_file:
                return existing_file.readlines()
        except FileNotFoundError:
            return []

    def apply(self):
        new_lines = [self._update_line(line) for line in self._get_current_file_lines()]
        for line_to_add in self._lines_to_add:
            line_to_add.self_insert_into(new_lines)
        with open(self.path, 'w') as new_file:
            new_file.writelines(new_lines)
