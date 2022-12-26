from __future__ import annotations
import os
import shutil
from .files import create_file_builder
ALL = "__all__"


class WorkingDirectory:
    """
    Singleton
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WorkingDirectory, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.previous_dirs = []

    @property
    def cwd(self):
        return os.getcwd()

    def get_all_files_or_dirs(self, ignore_dot_files=True):
        if ignore_dot_files:
            return [file_or_dir for file_or_dir in os.listdir(self.cwd) if file_or_dir[0] != "."]
        return os.listdir(self.cwd)

    @staticmethod
    def _build_path_if_not_exist(path: str):
        if not os.path.isdir(path):
            os.mkdir(path)

    @staticmethod
    def _not_move_in_self(destination, file_or_dir):
        return os.path.abspath(os.path.join(destination, file_or_dir)) != os.path.abspath(file_or_dir)

    def go_to(self, path: str):
        if os.path.isfile(path):
            raise FileExistsError("You can only use directory or non-existing paths for path!")
        self._build_path_if_not_exist(path)
        self.previous_dirs.append(self.cwd)
        os.chdir(path)

    def back(self):
        os.chdir(self.previous_dirs.pop())

    def go_to_home(self):
        self.go_to(self.previous_dirs[0])
        self.previous_dirs = []

    def transfer_with_files(self, new_path: str, files: list[str] or str = ALL):
        self.move_files(new_path, files)
        self.go_to(new_path)

    def transfer_and_copy_files(self, new_path: str, files: list[str] or str = ALL):
        self.copy_files(new_path, files)
        self.go_to(new_path)

    def move_file(self, new_path: str, file_or_dir_name: str, replace_if_exists=True):
        "Used to move file or dir."
        self._build_path_if_not_exist(new_path)
        new_path = os.path.join(new_path, file_or_dir_name)
        if os.path.abspath(file_or_dir_name) == os.path.abspath(new_path):
            return
        if replace_if_exists and os.path.isfile(new_path) or os.path.isdir(new_path):
            self.remove(new_path)
        shutil.move(file_or_dir_name, new_path)
        return new_path

    def move_files(self, new_path: str, files_or_dirs: list[str] or str = ALL, ignore_dot_files=True) -> list[str]:
        "Used to move files or dirs. If no files are specified will move everything from current dir."
        if files_or_dirs == ALL:
            files_or_dirs = self.get_all_files_or_dirs(ignore_dot_files)
        return [self.move_file(new_path, file_or_dir) for file_or_dir in files_or_dirs if self._not_move_in_self(new_path, file_or_dir)]

    def copy_file(self, new_path: str, file_or_dir_name: str, replace_if_exists=True) -> str:
        "Used to copy file or dir."
        self._build_path_if_not_exist(new_path)
        new_path = os.path.join(new_path, file_or_dir_name)
        if not replace_if_exists and os.path.isfile(new_path) or os.path.isdir(new_path):
            raise FileExistsError(f"{new_path} is present!")
        if os.path.abspath(file_or_dir_name) == os.path.abspath(new_path):
            return
        shutil.copytree(file_or_dir_name, new_path) if os.path.isdir(file_or_dir_name) \
            else shutil.copy(file_or_dir_name, new_path)
        return new_path

    def copy_files(self, new_path: str, files_or_dirs: list[str], ignore_dot_files=True, replace_if_exists=True) -> str:
        "Used to move files or dirs. If no files are specified will move everything from current dir."
        if files_or_dirs == ALL:
            files_or_dirs = self.get_all_files_or_dirs(ignore_dot_files)
        return [self.copy_file(new_path, file_or_dir, replace_if_exists) for file_or_dir in files_or_dirs if self._not_move_in_self(new_path, file_or_dir)]

    @staticmethod
    def remove(file_or_dir):
        shutil.rmtree(file_or_dir) if os.path.isdir(file_or_dir) else os.remove(file_or_dir)

    def __str__(self):
        return f"{self.__class__.__name__}<{self.cwd}>"

    def __repr__(self) -> str:
        return str(self)

    def __floordiv__(self, other) -> WorkingDirectory:
        self.go_to(str(other))
        return self

    def __truediv__(self, other) -> WorkingDirectory:
        self.go_to(str(other))
        return self

    def __add__(self, other) -> WorkingDirectory:
        self.go_to(str(other))
        return self

    def __sub__(self, other) -> WorkingDirectory:
        self.remove(other)
        return self

    def __setitem__(self, key: str, item):
        file_builder = create_file_builder(key)
        file_builder + item
        file_builder.save()

    def __getitem__(self, key: str):
        return create_file_builder(key).base_data
