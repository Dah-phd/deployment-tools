from deployment_tools.directory import WorkingDirectory
from pytest import fixture
import os

WD = WorkingDirectory()
TEST_LOCATION = 'new_location'
TEST_NEST_LOCATION = 'depth'
JSON_DATA = {'test': 'empty'}
JSON_NAME = 'test_wd.json'


def test_cfg_creation():
    WD[JSON_NAME] = JSON_DATA
    assert os.path.isfile(JSON_NAME)


def test_json_data():
    assert WD[JSON_NAME].base_data == JSON_DATA


def test_drop_file():
    WD.remove(JSON_NAME)
    assert not os.path.isfile(JSON_NAME)
