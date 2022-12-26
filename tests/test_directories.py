from deployment_tools.directory import WorkingDirectory
from pytest import fixture
import os

WD = WorkingDirectory()
TEST_LOCATION = 'new_location'
TEST_NEST_LOCATION = 'depth'
JSON_DATA = {'test': 'empty'}
JSON_NAME = 'test_wd.json'


def test_location_move():
    WD / TEST_LOCATION
    assert TEST_LOCATION in WD.cwd
    assert len(WD.previous_dirs) == 1
    WD.go_to_home()
    assert len(WD.previous_dirs) == 0


def test_move_with_files():
    WD / TEST_LOCATION
    WD[JSON_NAME] = JSON_DATA
    WD.transfer_with_files(TEST_NEST_LOCATION)
    assert TEST_NEST_LOCATION in WD.cwd
    assert WD.get_all_files_or_dirs() == [JSON_NAME]
    WD.back()
    assert TEST_NEST_LOCATION not in WD.cwd
    WD.go_to_home()
    assert TEST_LOCATION not in WD.cwd
    WD.remove(TEST_LOCATION)
    assert not os.path.isdir(TEST_LOCATION)


def test_copy_with_files():
    WD / TEST_LOCATION
    WD[JSON_NAME] = JSON_DATA
    WD.transfer_and_copy_files(TEST_NEST_LOCATION)
    assert TEST_NEST_LOCATION in WD.cwd
    assert WD.get_all_files_or_dirs() == [JSON_NAME]
    WD.back()
    assert TEST_NEST_LOCATION not in WD.cwd
    WD.go_to_home()
    assert TEST_LOCATION not in WD.cwd
    WD.remove(TEST_LOCATION)
    assert not os.path.isdir(TEST_LOCATION)


def test_cfg_creation():
    WD[JSON_NAME] = JSON_DATA
    assert os.path.isfile(JSON_NAME)


def test_json_data():
    assert WD[JSON_NAME] == JSON_DATA


def test_drop_file():
    WD.remove(JSON_NAME)
    assert not os.path.isfile(TEST_LOCATION)
