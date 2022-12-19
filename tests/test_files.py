from deployment_tools.files import FileTransformer, FileTransformationError
import json
import toml
import yaml
import os

TEST_JSON = 'test.json'
TEST_TOML = 'test.toml'
TEST_YAML = 'test.yml'
TEST_TXT = 'test.txt'
TEST_DATA = {'list': [1, 2, 3], 'number': 3, 'string': 'hello world!'}


def test_json_creation():
    test_json = FileTransformer(TEST_JSON)
    test_json += TEST_DATA
    test_json.save()
    with open(TEST_JSON, 'r') as data:
        assert json.load(data) == TEST_DATA


def test_toml_creation():
    test_toml = FileTransformer(TEST_TOML)
    test_toml + TEST_DATA
    test_toml.save()
    with open(TEST_TOML, 'r') as data:
        assert toml.load(data) == TEST_DATA


def test_yaml_creation():
    test_yaml = FileTransformer(TEST_YAML)
    test_yaml += TEST_DATA
    test_yaml.save()
    with open(TEST_YAML, 'r') as data:
        assert yaml.load(data, yaml.Loader) == TEST_DATA


def test_txt_creation():
    test_txt = FileTransformer(TEST_TXT)
    test_txt += ['asdad', 'new_line', 'last_line']
    test_txt.save()


def test_remove_files():
    FileTransformer(TEST_JSON).delete()
    FileTransformer(TEST_TOML).delete()
    FileTransformer(TEST_YAML).delete()
    assert (
        not os.path.isfile(TEST_JSON)
        and not os.path.isfile(TEST_TOML)
        and not os.path.isfile(TEST_YAML)
    )
