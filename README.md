# DEPLOYMENT-TOOLS
### Description:
Small package simplifying deployment scripts by:
* easy shell command running, with or without success checks;
* easy text file editing (such as configs, settings, etc ...);
* easy file file transfers;
### Content:
#### class Command => runs shell command from as list[str], example ["ls", "-la"]
* raise_on_failure() => raises ShellCommand exception on cmd failure;
* set_success(check:[str], on_line[int] = None) => check if string is present in outputs, could be specified specific line, where it should be (normal python indexing applies);
* set_failure(check:[str], on_line[int] = None) => check stderr for string, could be specified specific line, where it should be (normal python indexing applies);