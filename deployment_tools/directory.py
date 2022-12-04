from __future__ import annotations
import os
import shutil
from .files import FileTransformer
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

    def _get_all_files_or_dirs(self, ignore_dot_files=True):
        if ignore_dot_files:
            return [file_or_dir for file_or_dir in os.listdir(self.cwd) if file_or_dir[0] != "."]
        return os.listdir(self.cwd)

    def _target_withing_path(path: str, target: str) -> bool:
        return os.path.abspath(path) in os.path.abspath(target)

    def go_to(self, path: str):
        os.chdir(path)
        self.previous_dirs.append(self.cwd)

    def back(self):
        self.move_to(self.previous_dirs[-1])

    def transfer_with_files(self, path: str, files: list[str] or str = ALL):
        raise NotImplementedError()

    def transfer_and_copy_files(self, path: str, files: list[str] or str = ALL):
        raise NotImplementedError()

    def move_file(self, path: str, file_or_dir_name: str, replace_if_exists=True):
        "Used to move file or dir."
        new_path = os.path.join(path, file_or_dir_name)
        if replace_if_exists and os.path.isfile(new_path) or os.path.isdir(new_path):
            self.remove(new_path)
        if os.path.abspath(file_or_dir_name) != os.path.abspath(new_path):
            shutil.move(file_or_dir_name, new_path)
        return new_path

    def move_files(self, path: str, files_or_dirs: list[str] or str = ALL, ignore_dot_files=True) -> list[str]:
        "Used to move files or dirs. If no files are specified will move everything from current dir."
        if files_or_dirs == ALL:
            files_or_dirs = self._get_all_files_or_dirs(ignore_dot_files)
        return [self.move_file(path, file_or_dir) for file_or_dir in files_or_dirs]

    def copy_file(self, path: str, file_or_dir_name: str, replace_if_exists=True) -> str:
        "Used to copy file or dir."
        new_path = os.path.join(path, file_or_dir_name)
        if not replace_if_exists and os.path.isfile(new_path) or os.path.isdir(new_path):
            raise FileExistsError(f"{new_path} is present!")
        if os.path.abspath(file_or_dir_name) != os.path.abspath(new_path):
            shutil.copytree(file_or_dir_name, new_path) if os.path.isdir(file_or_dir_name) \
                else shutil.copy(file_or_dir_name, new_path)
        return new_path

    def copy_files(self, path: str, files_or_dirs: list[str], ignore_dot_files=True, replace_if_exists=True) -> str:
        "Used to move files or dirs. If no files are specified will move everything from current dir."
        if files_or_dirs == ALL:
            files_or_dirs = self._get_all_files_or_dirs(ignore_dot_files)
        return [self.copy_file(path, file_or_dir, replace_if_exists) for file_or_dir in files_or_dirs]

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

    def __setitem__(self, path: str, lines: list[str] or str):
        if isinstance(lines, list) or isinstance(lines, str):
            FileTransformer(path).add_line(lines).save()
        raise TypeError("UNSUPORTED ASSIGNMENT!")

    def __getitem__(self, path: str) -> str or FileTransformer:
        if os.path.isdir(path):
            return os.path.abspath(path)
        return FileTransformer(path)


if __name__ == "__main__":
    wd = WorkingDirectory()
    wd.copy_file("tests", "test.txt")
    print(wd)
