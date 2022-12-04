from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import json
import toml
import yaml
from pprint import pprint
from os.path import isfile


class FileTransformationError(Exception):
    pass


class _FileType(Enum):
    JSON = json.load
    YAML = lambda reader: yaml.load(reader, Loader=yaml.Loader)
    TOML = toml.load
    TEXT = lambda reader: reader.readlines()

    @staticmethod
    def get_writer_callback(file_type: _FileType) -> function:
        return {
            _FileType.JSON: lambda data, writer: json.dump(data, writer, indent=4),
            _FileType.YAML: lambda data, writer: yaml.dump(data, writer, indent=2, Dumper=yaml.Dumper),
            _FileType.TOML: lambda data, writer: toml.dump(data, writer),
            _FileType.TEXT: lambda data, writer: writer.writelines(data)
        }[file_type]

    @classmethod
    def get_type(cls, path: str) -> _FileType:
        ext = path.split('.')[-1].lower()
        if ext == 'json':
            return cls.JSON
        if ext in ['yml', 'yaml']:
            return cls.YAML
        if ext == 'toml':
            return cls.TOML
        return cls.TEXT

    @staticmethod
    def stringify(file_type: _FileType):
        if file_type is _FileType.JSON:
            return "JSON"
        if file_type is _FileType.YAML:
            return "YAML"
        if file_type is _FileType.TOML:
            return "TOML"
        return "TEXT"


class FileTransformer:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._out_path: str = path
        self.file_type = _FileType.get_type(path)
        self._updates = []

    def __set_path(self, path: str or None):
        if path is not None:
            self._out_path = path

    def __raise_transformation_err(self):
        if self.file_type is _FileType.TEXT:
            raise FileTransformationError(f"Unable to parse TEXT file tree to {_FileType.stringify(self.file_type)}")

    def to_json(self, path: str = None):
        self.__raise_transformation_err()
        self.__set_path(path)
        self.file_type = _FileType.JSON

    def to_toml(self, path: str = None):
        self.__raise_transformation_err()
        self.__set_path(path)
        self.file_type = _FileType.TOML

    def to_yaml(self, path: str = None):
        self.__raise_transformation_err()
        self.__set_path(path)
        self.file_type = _FileType.YAML

    @staticmethod
    def __ensure_newline(line: str) -> str:
        if not line.endswith('\n'):
            line += '\n'
        return line

    def add_update_with_list_appends(self, update: dict):
        self.__transform_lists_to_tuples_in_dict(update)
        self._updates.append(update)

    def __transform_lists_to_tuples_in_dict(self, data: dict):
        for key, val in data:
            if isinstance(val, dict):
                self.__transform_lists_to_tuples_in_dict(val)
            if isinstance(val, list):
                data[key] = tuple(val)

    def save(self, data):
        file_data = self._read()
        write = _FileType.get_writer_callback(self.file_type)
        if file_data is not None:
            new_lines = [self.__update_line(line) for line in self.__reader()]
            for line_to_add in self._lines_to_add:
                line_to_add.self_insert_into(new_lines)
            with open(self._path, 'w') as new_file:
                new_file.writelines(new_lines)
        with open(self._out_path, 'w') as target:
            write(data, target)

    def __getitem__(self, key: str) -> FileTransformer:
        return FileTransformer(key)

    def __setitem__(self, key: str, item):
        ft = FileTransformer(key)

    def __sub__(self, other):
        NotImplementedError()
        return self

    def __add__(self, other):
        if not isinstance(other, str) and not isinstance(other, dict) and not isinstance(list):
            raise TypeError(f"Unsuported type: {type(other)} by + operand. You can use dict or str or list.")
        if isinstance(other, list):
            for el in other:
                if not isinstance(el, str) and not isinstance(el, dict):
                    raise TypeError(
                        f"Unsuported type: {type(other)} by + operand. You can use dict or str in list of updates."
                    )
        self._updates.append(other)
        return self

    def _read(self) -> dict or list or None:
        if not isfile(self.path):
            return None
        with open(self.path, 'r') as data:
            try:
                return self.file_type(data)
            except Exception as e:
                print(e)
                print("====> reading as text ...")
                return _FileType.TEXT(data)

    def __update_keys_in_dict(self, base: dict, new: dict):
        for key, val in new.items():
            if key not in base:
                base[key] = val
            elif isinstance(val, dict):
                self.__update_keys_in_dict(base[key], val)
            elif isinstance(val, tuple):
                base[key] += list(val)
            else:
                base[key] = val


if __name__ == '__main__':
    FileTransformer("new_json.json").save({"asd": 123})
