# DEPLOYMENT-TOOLS
### Description:
Small package simplifying deployment scripts by:
* easy shell command running, with or without success checks;
* easy file editing (such as configs, settings, text, etc ...);
* easy file transfers, directory manipulation, and file reading;
### Content:
#### class Command => runs shell command from as list[str], example ["ls", "-la"]
* raise_on_failure() => raises ShellCommand exception on cmd failure;
* set_success(check:[str], on_line[int] = None) => check if string is present in outputs, could be specified specific line, where it should be (normal python indexing applies);
* set_failure(check:[str], on_line[int] = None) => check stderr for string, could be specified specific line, where it should be (normal python indexing applies);
#### class [File]Builder:
* invoked by create_file_builder(path: str, type_: str | None = None, blanked=False) => path - location of the file, type_ - if None, the function will decide based on extension, otherwise supported are json, toml, yaml/yml, or it will default to txt; blanked - will void the data in the file;
* attribute self.base_data, holds all the file information;
* [+]/[-] operand can be used to either add or remove from the files (including nesting of dicts in cases of nested configs);
* txt files support self.replace_line(patten, new_line) if pattern in existing line, it will be replaced by new_line;
* self.replace_string_in_lines(old, new), it will replace old:str with new:str in all occurances in the files;
#### class WorkingDirectory (singleton):
* slicing: [file_name] -> returns file content as dict(json, yml/yaml, toml) or list;
* setting: [file_name] = payload: str|list -> create file with provided data;
* [+]/[/]/[self.go_to(path)] - operands are used to transfer exectusion to another location;
* self.back() - return to previous location;
* self.go_to_home() - return to initial location;
* self.transfer_with_files(*args) => move execution to a location with all files in current location;
* self.transfer_and_copy_files(*args) => move execution to a location copy all files in current location;