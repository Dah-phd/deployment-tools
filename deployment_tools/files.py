from __future__ import annotations
from enum import Enum
from io import TextIOWrapper
import json
import toml
import yaml
from os import path, remove


class FileTransformationError(Exception):
    pass


class _BaseBuilder:
    def __init__(self, path: str, updates: list) -> None:
        self.path = path
        self.updates: list = updates
        self.base_data: list | dict = self._read()
        self._make_updates()
        self.base_data = self.post_processing(self.base_data)
        self._write()

    def _read(self) -> dict | list | None:
        if not path.isfile(self.path):
            return []
        with open(self.path, 'r') as file_object:
            return self.loader(file_object)

    def loader(self, file_object: TextIOWrapper) -> dict | list:
        NotImplementedError()

    def _write(self):
        with open(self.path, 'w') as file_object:
            return self.writer(self.base_data, file_object)

    def writer(self, new_data: dict | list, file_object: TextIOWrapper):
        NotImplementedError()

    def post_processing(self, base_data) -> list | dict:
        return base_data

    def _make_updates(self):
        for update in self.updates:
            self.base_data = self.recursive_update(self.base_data, update)

    def recursive_update(self, base_data: dict | list, update) -> dict | list:
        raise NotImplementedError()


class JsonBuilder(_BaseBuilder):
    def loader(self, file_object: TextIOWrapper):
        return json.load(file_object)

    def writer(self, new_data: dict | list, file_object: TextIOWrapper):
        return json.dump(new_data, file_object, indent=4)

    def recursive_update(self, data: dict | list, update):
        if isinstance(data, dict):
            if isinstance(update, list):
                for upd_part in update:
                    data = self.recursive_update(data, upd_part)
            if isinstance(update, dict):
                for k, v in update.items():
                    data[k] = v if k not in data else self.recursive_update(data[k], v)
        if isinstance(data, list):
            if not data:
                return update
            if isinstance(update, tuple):
                return list(update)
            if isinstance(update, list):
                data.extend(update)
            data.append(update)
        return data


class TomlBuilder(_BaseBuilder):
    def loader(self, file_object: TextIOWrapper):
        return toml.load(file_object)

    def writer(self, new_data: dict | list, file_object: TextIOWrapper):
        return toml.dump(new_data, file_object)

    def recursive_update(self, data: dict | list, update):
        if isinstance(data, dict):
            if isinstance(update, list):
                for upd_part in update:
                    data = self.recursive_update(data, upd_part)
            if isinstance(update, dict):
                for k, v in update.items():
                    data[k] = v if k not in data else self.recursive_update(data[k], v)
        if isinstance(data, list):
            if not data:
                return update
            if isinstance(update, tuple):
                return list(update)
            if isinstance(update, list):
                data.extend(update)
            data.append(update)
        return data


class YamlBuilder(_BaseBuilder):
    def loader(self, file_object: TextIOWrapper):
        return yaml.load(file_object, yaml.Loader)

    def writer(self, new_data: dict | list, file_object: TextIOWrapper):
        return yaml.dump(new_data, file_object, indent=2, Dumper=yaml.Dumper)

    def recursive_update(self, data: dict | list, update):
        if isinstance(data, dict):
            if isinstance(update, list):
                for upd_part in update:
                    data = self.recursive_update(data, upd_part)
            if isinstance(update, dict):
                for k, v in update.items():
                    data[k] = v if k not in data else self.recursive_update(data[k], v)
        if isinstance(data, list):
            if not data:
                return update
            if isinstance(update, tuple):
                return list(update)
            if isinstance(update, list):
                data.extend(update)
            data.append(update)
        return data


class TxtBuilder(_BaseBuilder):
    def loader(self, file_object: TextIOWrapper) -> list:
        return file_object.readlines()

    def writer(self, new_data: list, file_object: TextIOWrapper):
        file_object.writelines(new_data)

    def recursive_update(self, base_data: list[str], update) -> dict | list:
        if isinstance(update, tuple):
            if isinstance(update[0], int):
                base_data[update[0]] = update[1]
            if isinstance(update[0], str):
                base_data = [line.replace(update[0], update[1]) for line in base_data]
        elif isinstance(update, dict):
            for k, v in update.items():
                base_data = [line if k not in line else v for line in base_data]
        elif isinstance(update, list):
            base_data.extend(update)
        else:
            base_data.append(str(update))
        return base_data

    def post_processing(self, base_data: list[str]) -> list:
        return [line if line.endswith('\n') else f'{line}\n' for line in base_data]


class FileBuilder:
    file_types = {
        "json": JsonBuilder,
        "toml": TomlBuilder,
        "yml": YamlBuilder,
        "yaml": YamlBuilder
    }

    def __init__(self, path: str, type_: str | None = None) -> None:
        self.path = path
        self.updates = []
        self.type_ = self.path.split('.')[-1].lower() if type_ is None else type_
        self.Builder = self.file_types.get(self.type_, TxtBuilder)

    def __add__(self, other) -> FileBuilder:
        self.updates.append(other)
        return self

    def delete(self):
        if path.isfile(self.path):
            remove(self.path)

    def save(self):
        self.Builder(self.path, self.updates)
