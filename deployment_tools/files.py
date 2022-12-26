from __future__ import annotations
from io import TextIOWrapper
from copy import deepcopy
import json
import toml
import yaml
from os import path, remove


class FileTransformationError(Exception):
    pass


class _BaseBuilder:
    _default = dict

    def __init__(self, path: str, blanked=False) -> None:
        self.path = path
        self.base_data: list | dict = self._read(blanked)

    def _read(self, blanked: bool) -> dict | list | None:
        if not path.isfile(self.path) or blanked:
            return self._default()
        with open(self.path, 'r') as file_object:
            return self._load(file_object)

    def _load(self, file_object: TextIOWrapper) -> dict | list:
        NotImplementedError()

    def _write(self):
        with open(self.path, 'w') as file_object:
            return self._dump(self.base_data, file_object)

    def _dump(self, new_data: dict | list, file_object: TextIOWrapper):
        NotImplementedError()

    def _post_processing(self, base_data) -> list | dict:
        return base_data

    def __getitem__(self, key) -> dict | str | list:
        return self.base_data[key]

    def __setitem__(self, key, value):
        self.base_data[key] = value

    def __add__(self, other) -> _BaseBuilder:
        self._handle_addition(self.base_data, deepcopy(other))
        return self

    def _handle_addition(self, base, other):
        if not base:
            self.replace_all_data(other)
            return
        match base:
            case dict(base):
                if isinstance(other, dict):
                    for key, value in other.items():
                        if key in base:
                            if isinstance(value, dict):
                                self._handle_addition(base[key], value)
                            else:
                                base[key] = value
                        else:
                            base[key] = value
                else:
                    raise TypeError(f"Unsupported operand ('+') for type: {type(other)}!")
            case list(base): base.extend(other) if isinstance(other, list) else base.append(other)

    def __sub__(self, other) -> _BaseBuilder:
        self._handle_subtraction(self.base_data, deepcopy(other))
        return self

    def _handle_subtraction(self, base, other):
        match base:
            case dict(base):
                if isinstance(other, dict):
                    for key, value in other.items():
                        self._handle_subtraction(base[key], value)
                else:
                    del base[other]
            case list(base):
                match other:
                    case int(idx): del base[idx]
                    case str(pattern): self.replace_all_data([line for line in base if pattern not in line])
                    case _: raise TypeError(f"Unsupported operand ('-') for type: {type(other)}!")

    def replace_all_data(self, value: list | dict):
        self.base_data = deepcopy(value)

    def save(self):
        self.base_data = self._post_processing(self.base_data)
        self._write()

    def delete(self):
        if path.isfile(self.path):
            remove(self.path)


class JsonBuilder(_BaseBuilder):
    def _load(self, file_object: TextIOWrapper):
        return json.load(file_object)

    def _dump(self, new_data: dict | list, file_object: TextIOWrapper):
        return json.dump(new_data, file_object, indent=4)


class TomlBuilder(_BaseBuilder):
    def _load(self, file_object: TextIOWrapper):
        return toml.load(file_object)

    def _dump(self, new_data: dict | list, file_object: TextIOWrapper):
        return toml.dump(new_data, file_object)

    def _post_processing(self, base_data) -> list | dict:
        if not isinstance(base_data, dict):
            raise TypeError(f'Toml can only be build from dict! The proveded base is of type {type(base_data)}!')
        return base_data


class YamlBuilder(_BaseBuilder):
    def _load(self, file_object: TextIOWrapper):
        return yaml.load(file_object, yaml.Loader)

    def _dump(self, new_data: dict | list, file_object: TextIOWrapper):
        return yaml.dump(new_data, file_object, indent=2, Dumper=yaml.Dumper)


class TxtBuilder(_BaseBuilder):
    _default = list

    def _load(self, file_object: TextIOWrapper) -> list:
        return file_object.readlines()

    def _dump(self, new_data: list, file_object: TextIOWrapper):
        file_object.writelines(new_data)

    def replace_line(self, pattern: str, new_line: str) -> int:
        new_lines = 0
        for idx, line in enumerate(self.base_data):
            if pattern in line:
                self.base_data[idx] = new_line
                new_lines += 1
        return new_lines

    def replace_string_in_lines(self, old: str, new: str) -> int:
        replaces = 0
        for idx, line in enumerate(self.base_data):
            if old in line:
                self.base_data[idx] = line.replace(old, new)
                replaces += 1
        return replaces

    def _handle_addition(self, base: list[str], other):
        match other:
            case dict(replace_lines):
                for pat, new_line in replace_lines.items():
                    self.replace_line(pat, new_line)
            case list(new_lines):
                base.extend(new_lines)
            case _:
                base.append(other)

    def _post_processing(self, base_data: list[str]) -> list:
        return [line if line.endswith('\n') else f'{line}\n' for line in base_data]


def create_file_builder(path: str, type_: str | None = None, blanked=False) -> JsonBuilder | TomlBuilder | YamlBuilder | TxtBuilder:
    type_ = path.split('.')[-1].lower() if type_ is None else type_
    return {
        "json": JsonBuilder,
        "toml": TomlBuilder,
        "yml": YamlBuilder,
        "yaml": YamlBuilder
    }.get(type_, TxtBuilder)(path, blanked)
