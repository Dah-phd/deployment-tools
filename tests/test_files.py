from deployment_tools.files import create_file_builder
import pytest
import json
import toml
import yaml
import os


class TestCaseDictType():
    TEST_DATA = {'list': [3], 'number': 3, 'string': 'hello world!'}
    TEST_DATA_LIST = ["1", "2", "3", {'hello': 'world', 'list': [1, 2, 3]}]
    TEST_UPDATE = {'new_key': 'new_data'}
    TEST_JSON = 'test.json'
    TEST_TOML = 'test.toml'
    TEST_YAML = 'test.yml'
    TEST_TXT = 'test.txt'

    def create_complex_dict_type_and_check(self, path: str, loader, check_dict: dict = None):
        check_dict = check_dict if check_dict is not None else {'1': 1, '2': 2}
        test_file = create_file_builder(path, blanked=True)
        test_file + self.TEST_DATA_LIST
        test_file + "asd"
        test_file + {1: 1, 2: 2}
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data) == self.TEST_DATA_LIST + ['asd', check_dict]

    def create_dict_type_file_and_check(self, path: str, loader):
        test_file = create_file_builder(path)
        test_file + self.TEST_DATA
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data) == self.TEST_DATA

    def update_dict_type_file_and_check(self, path: str, loader):
        test_file = create_file_builder(path)
        test_file + self.TEST_UPDATE
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data) == {**self.TEST_DATA, **self.TEST_UPDATE}

    @staticmethod
    def update_existing_key_and_check(path: str, loader):
        test_file = create_file_builder(path)
        test_file + {'list': [4, 5]}
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data)['list'] == [4, 5]

    @staticmethod
    def check_content(path: str, loader, slice='list'):
        test_file = create_file_builder(path)
        with open(path, 'r') as data:
            assert loader(data)[slice] == test_file[slice]

    @staticmethod
    def remove_and_check(path):
        create_file_builder(path).delete()
        assert not os.path.isfile(path)

    @staticmethod
    def subtract_and_check(path: str, loader, slice: str = 'number'):
        test_file = create_file_builder(path)
        assert slice in test_file.base_data
        test_file - slice
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data).get(slice) is None

    @staticmethod
    def yml_loader(path):
        return yaml.load(path, yaml.Loader)

    def test_json_create(self):
        self.create_dict_type_file_and_check(self.TEST_JSON, json.load)

    def test_json_update(self):
        self.update_dict_type_file_and_check(self.TEST_JSON, json.load)

    def test_json_update_existing_key(self):
        self.update_existing_key_and_check(self.TEST_JSON, json.load)

    def test_json_content(self):
        self.check_content(self.TEST_JSON, json.load)

    def test_json_subtract(self):
        self.subtract_and_check(self.TEST_JSON, json.load)

    def test_json_complex_create(self):
        self.create_complex_dict_type_and_check(self.TEST_JSON, json.load)

    def test_json_complex_content(self):
        self.check_content(self.TEST_JSON, json.load, 3)

    def test_toml_create(self):
        self.create_dict_type_file_and_check(self.TEST_TOML, toml.load)

    def test_toml_update(self):
        self.update_dict_type_file_and_check(self.TEST_TOML, toml.load)

    def test_toml_update_existing_key(self):
        self.update_existing_key_and_check(self.TEST_TOML, toml.load)

    def test_toml_content(self):
        self.check_content(self.TEST_TOML, toml.load)

    def test_toml_subtract(self):
        self.subtract_and_check(self.TEST_TOML, toml.load)

    def test_toml_complex_create(self):
        with pytest.raises(TypeError):
            self.create_complex_dict_type_and_check(self.TEST_TOML, toml.load)

    def test_yaml_create(self):
        self.create_dict_type_file_and_check(self.TEST_YAML, self.yml_loader)

    def test_yaml_update(self):
        self.update_dict_type_file_and_check(self.TEST_YAML, self.yml_loader)

    def test_yaml_update_existing_key(self):
        self.update_existing_key_and_check(self.TEST_YAML, self.yml_loader)

    def test_yaml_content(self):
        self.check_content(self.TEST_YAML, self.yml_loader)

    def test_yaml_subtract(self):
        self.subtract_and_check(self.TEST_YAML, self.yml_loader)

    def test_yaml_complex_create(self):
        self.create_complex_dict_type_and_check(self.TEST_YAML, self.yml_loader, check_dict={1: 1, 2: 2})

    def test_txt_creation(self):
        test_txt = create_file_builder(self.TEST_TXT)
        lines = ["first_line", "second_line"]
        third_line = "third line\n"
        test_txt + lines
        test_txt + third_line
        test_txt + ['replace', 'new_line', 'end']
        test_txt.save()
        with open(self.TEST_TXT, 'r') as txt:
            assert txt.readlines()[:3] == [line + '\n' for line in lines] + [third_line]

    def test_txt_content(self):
        test_txt = create_file_builder(self.TEST_TXT)
        with open(self.TEST_TXT, 'r') as txt:
            assert txt.readlines()[2] == test_txt[2]

    def test_txt_drop(self):
        test_txt = create_file_builder(self.TEST_TXT)
        count = len(test_txt.base_data) - 1
        test_txt - 'third'
        test_txt.save()
        with open(self.TEST_TXT, 'r') as txt:
            assert len(txt.readlines()) == count

    def test_txt_drop_idx(self):
        test_txt = create_file_builder(self.TEST_TXT)
        count = len(test_txt.base_data) - 1
        test_txt - 1
        test_txt.save()
        with open(self.TEST_TXT, 'r') as txt:
            assert len(txt.readlines()) == count

    def test_replace_line(self):
        replace = 'test_worked_correctly\n'
        test_txt = create_file_builder(self.TEST_TXT)
        assert test_txt.replace_line('new_l', replace) == 1
        test_txt.save()
        with open(self.TEST_TXT, 'r') as txt:
            assert replace in txt.readlines()

    def test_replace_str(self):
        test_txt = create_file_builder(self.TEST_TXT)
        old = 'place'
        assert test_txt.replace_string_in_lines(old, 'work') == 1
        test_txt.save()
        with open(self.TEST_TXT, 'r') as txt:
            assert not [line for line in txt.readlines() if old in line]

    def test_delete_and_cleanup(self):
        self.remove_and_check(self.TEST_JSON)
        self.remove_and_check(self.TEST_YAML)
        self.remove_and_check(self.TEST_TOML)
        self.remove_and_check(self.TEST_TXT)
