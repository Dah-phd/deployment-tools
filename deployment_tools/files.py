from __future__ import annotations
from copy import deepcopy
from io import TextIOWrapper
import json
import toml
import yaml
from os import path, remove


class FileTransformationError(Exception):
    pass


class _BaseBuilder:
    def __init__(self, path: str, updates: list, blanked=False) -> None:
        self.path = path
        self.updates: list = updates
        self.base_data: list | dict = self._read(blanked)
        self._make_updates()
        self.base_data = self.post_processing(self.base_data)
        self._write()

    def _read(self, blanked: bool) -> dict | list | None:
        if not path.isfile(self.path) or blanked:
            return None
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

    def handle_dict_base(self, data: dict, update):
        match update:
            case list(update):
                for upd_part in update:
                    data = self.recursive_update(data, upd_part)
            case dict(update):
                for key, val in update.items():
                    data[key] = val if key not in data else self.recursive_update(data[key], val)
        return data

    def handle_list_base(self, data: list, update):
        match update:
            case {"index": int(idx), "value": val}: data[idx] = val
            case tuple(update): data = update[0] if len(update) == 1 else list(update)
            case list(update): data.extend(update)
            case _: data.append(update)
        return data

    def recursive_update(self, data: dict | list, update):
        if not data:
            return update
        if isinstance(data, dict):
            return self.handle_dict_base(data, update)
        if isinstance(data, list):
            return self.handle_list_base(data, update)
        return data


class JsonBuilder(_BaseBuilder):
    def loader(self, file_object: TextIOWrapper):
        return json.load(file_object)

    def writer(self, new_data: dict | list, file_object: TextIOWrapper):
        return json.dump(new_data, file_object, indent=4)


class TomlBuilder(_BaseBuilder):
    def loader(self, file_object: TextIOWrapper):
        return toml.load(file_object)

    def writer(self, new_data: dict | list, file_object: TextIOWrapper):
        if not isinstance(new_data, dict):
            raise TypeError("Toml file cannot be built from a list form data, only DICT data!")
        return toml.dump(new_data, file_object)

    def post_processing(self, base_data) -> list | dict:
        if not isinstance(base_data, dict):
            raise TypeError(f'Toml can only be build from dict! The proveded base is of type {type(base_data)}!')
        return base_data


class YamlBuilder(_BaseBuilder):
    def loader(self, file_object: TextIOWrapper):
        return yaml.load(file_object, yaml.Loader)

    def writer(self, new_data: dict | list, file_object: TextIOWrapper):
        return yaml.dump(new_data, file_object, indent=2, Dumper=yaml.Dumper)


class TxtBuilder(_BaseBuilder):
    def loader(self, file_object: TextIOWrapper) -> list:
        return file_object.readlines()

    def writer(self, new_data: list, file_object: TextIOWrapper):
        file_object.writelines(new_data)

    def recursive_update(self, base_data: list[str], update) -> list:
        if not base_data:
            return update
        match update:
            case list(update): base_data.extend(update)
            case [int(idx), new_line]: base_data[idx] = new_line
            case [str(old_str), str(new_str)]: base_data = [line.replace(old_str, new_str) for line in base_data]
            case dict(update):
                for k, v in update.items():
                    base_data = [line if k not in line else v for line in base_data]
            case _: base_data.append(str(update))
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

    def __init__(self, path: str, type_: str | None = None, blanked=False) -> None:
        self.path = path
        self.blanked = blanked
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
        self.Builder(self.path, deepcopy(self.updates), self.blanked)

    def set_value_in_list_config(self, index: int, value):
        """
            Used to place value at position in list-type configs.
            You can directly use self += {"index":i, "value":v}
        """
        if isinstance(self.Builder, YamlBuilder) or isinstance(self.Builder, JsonBuilder):
            self.updates.append({"index": index, "value": value})

    def replace_in_txt_file(self, old_str: str, new_str: str):
        """
            Replace string in all lines, you can directly use self += (old, new)
        """
        self.updates.append((old_str, new_str))

    def set_config_update_with_list_override(self, update):
        if isinstance(update, dict):
            for k, v in update.items():
                update[k] = self.set_config_update_with_list_override(v)
        elif isinstance(update, list):
            update = tuple(update)
        else:
            update = (update,)
        self.updates.append(update)
