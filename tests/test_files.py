from deployment_tools.files import FileTransformationError, FileBuilder
import json
import toml
import yaml
import os


class TestCaseDictType():
    TEST_DATA = {'list': [1, 2, 3], 'number': 3, 'string': 'hello world!'}
    TEST_DATA_LIST = [1, 2, 3, {'hello': 'world', 'list': [1, 2, 3]}]
    TEST_UPDATE = {'new_key': 'new_data'}
    TEST_JSON = 'test.json'
    TEST_TOML = 'test.toml'
    TEST_YAML = 'test.yml'
    TEST_TXT = 'test.txt'

    def create_complex_dict_type_and_check(self, path: str, loader):
        test_file = FileBuilder(path)
        test_file += self.TEST_DATA_LIST
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data) == self.TEST_DATA_LIST
        # self.remove_and_check(path)

    def create_dict_type_file_and_check(self, path: str, loader):
        test_file = FileBuilder(path)
        test_file += self.TEST_DATA
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data) == self.TEST_DATA

    def update_dict_type_file_and_check(self, path: str, loader):
        test_file = FileBuilder(path)
        test_file += self.TEST_UPDATE
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data) == {**self.TEST_DATA, **self.TEST_UPDATE}

    @staticmethod
    def update_list_without_replacing_and_check(path: str, loader):
        test_file = FileBuilder(path)
        test_file.add_update_with_list_appends({'list': [4]})
        test_file.add_update_with_list_appends({'list': [5]})
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data)['list'] == [1, 2, 3, 4, 5]

    @staticmethod
    def update_existing_key_and_check(path: str, loader):
        test_file = FileBuilder(path)
        test_file += {'list': [4, 5]}
        test_file.save()
        with open(path, 'r') as data:
            assert loader(data)['list'] == [4, 5]

    @staticmethod
    def remove_and_check(path):
        FileBuilder(path).delete()
        assert not os.path.isfile(path)

    def test_json(self):
        self.create_dict_type_file_and_check(self.TEST_JSON, json.load)
        self.update_dict_type_file_and_check(self.TEST_JSON, json.load)
        # self.update_list_without_replacing_and_check(self.TEST_JSON, json.load)
        self.update_existing_key_and_check(self.TEST_JSON, json.load)

    def test_toml(self):
        self.create_dict_type_file_and_check(self.TEST_TOML, toml.load)
        self.update_dict_type_file_and_check(self.TEST_TOML, toml.load)
        # self.update_list_without_replacing_and_check(self.TEST_TOML, toml.load)
        self.update_existing_key_and_check(self.TEST_TOML, toml.load)

    def test_yaml(self):
        def loader(path):
            return yaml.load(path, yaml.Loader)
        self.create_dict_type_file_and_check(self.TEST_YAML, loader)
        self.update_dict_type_file_and_check(self.TEST_YAML, loader)
        # self.update_list_without_replacing_and_check(self.TEST_YAML, loader)
        self.update_existing_key_and_check(self.TEST_YAML, loader)

    def test_txt_creation(self):
        test_txt = FileBuilder(self.TEST_TXT)
        lines = ["first_line", "second_line"]
        third_line = "third line\n"
        test_txt += lines
        test_txt += third_line
        test_txt.save()
        with open(self.TEST_TXT, 'r') as txt:
            assert txt.readlines() == [line + '\n' for line in lines] + [third_line]

    def test_remove(self):
        self.remove_and_check(self.TEST_JSON)
        self.remove_and_check(self.TEST_YAML)
        self.remove_and_check(self.TEST_TOML)
        self.remove_and_check(self.TEST_TXT)
