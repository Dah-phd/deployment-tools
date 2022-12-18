from __future__ import annotations
from enum import Enum
import json
import toml
import yaml
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
        self.__file_type = _FileType.get_type(path)
        self.__out_type = self.__file_type
        self._updates = []
        self._replaces = []
        self._removals = []

    @classmethod
    def create_file(cls, path, data):
        fs = cls(path) + data
        fs.save()

    def __set_path(self, path: str or None):
        if path is not None:
            self._out_path = path

    def __raise_transformation_err(self):
        if self.__file_type is _FileType.TEXT:
            raise FileTransformationError(f"Unable to parse TEXT file tree to {_FileType.stringify(self.__file_type)}")

    def to_json(self, path: str = None):
        self.__raise_transformation_err()
        self.__set_path(path)
        self.__out_type = _FileType.JSON

    def to_toml(self, path: str = None):
        self.__raise_transformation_err()
        self.__set_path(path)
        self.__out_type = _FileType.TOML

    def to_yaml(self, path: str = None):
        self.__raise_transformation_err()
        self.__set_path(path)
        self.__out_type = _FileType.YAML

    def to_text(self, path: str = None):
        self.__set_path(path)
        self.__out_type = _FileType.JSON

    def add_update_with_list_appends(self, update: dict):
        self.__transform_lists_to_tuples_in_dict(update)
        self._updates.append(update)

    def replace_in_text_file(self, old: str, new: str):
        """
        This method can be used only for text files
        """
        self._replaces.append((old, new))

    def __transform_lists_to_tuples_in_dict(self, data: dict):
        for key, val in data:
            if isinstance(val, dict):
                self.__transform_lists_to_tuples_in_dict(val)
            if isinstance(val, list):
                data[key] = tuple(val)

    def save(self):
        file_data = self._read()
        write = _FileType.get_writer_callback(self.__file_type)
        if isinstance(file_data, dict):
            self.__update_config_file_lines(file_data)
        if isinstance(file_data, list):
            self.__update_text_file_lines(file_data)
        with open(self._out_path, 'w') as target:
            write(file_data, target)

    def __update_config_file_lines(self, file_data: dict):
        for update in self._updates:
            self.__update_keys_in_dict(file_data, update)
        for removal in self._removals:
            if removal in file_data:
                del file_data[removal]

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

    def __update_text_file_lines(self, file_data: list[str]):
        new_lines = []
        drop_list = []
        for idx, line in enumerate(file_data):
            new_lines += self.__apply_updates_in_text_line(file_data, idx, line)
            for replace in self._replaces:
                file_data[idx] = line.replace(replace[0], replace[1])
            for removal in self._removals:
                if removal in line:
                    drop_list.append(line)
        for drop in set(drop_list):
            file_data.remove(drop)
        file_data.extend(new_lines)

    def __apply_updates_in_text_line(self, file_data: list[str], idx: int, line: str):
        new_lines = []
        for update in self._updates:
            if isinstance(update, dict):
                for key, new_line in update.items():
                    if key in line:
                        file_data[idx] = self.__ensure_newline(new_line)
            if isinstance(update, str):
                new_lines.append(self.__ensure_newline(update))
        return new_lines

    def __getitem__(self, key: str) -> FileTransformer:
        return FileTransformer(key)

    def __setitem__(self, key: str, item):
        ft = FileTransformer(key).__add__({key: item})

    def __sub__(self, other: str):
        if not isinstance(other, str):
            raise TypeError("Subtraction supports only string at the moment - defining key or pattern to be dropped.")
        self._removals.append(other)
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
            return [] if self.__file_type is _FileType.TEXT else dict()
        with open(self.path, 'r') as data:
            try:
                return self.__file_type(data)
            except Exception as e:
                self.__file_type = _FileType.TEXT
                self.__out_type = _FileType.TEXT
                print(e)
                print("====> reading as text ...")
                return self.__file_type(data)

    @staticmethod
    def __ensure_newline(line: str) -> str:
        if not line.endswith('\n'):
            line += '\n'
        return line


if __name__ == '__main__':
    FileTransformer("new_json.json").save()
