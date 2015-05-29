# Makemake

Makefile Generator

For each source file generate a rule and look for dependencies (included files)

### Usage

To update or create a new Makefile:

`makemake`;

Makemake will prompt you for config

### Rules

Makefile rules:
* `all` (First rule) Depend `$(NAME)` rule
* `$(NAME)` Depend `$(O_FILES)` rules and link the final binary (Also depend `$(LIBS)`)
* `$(O_FILES)` Compile an object file (Also depend `.h`, `.hpp` or other included files)
* `clean` Clean objects files
* `fclean` Depend `clean` and remove the binary
* `re` Depend `fclean` and `all`

### Config

The config is stored at the top of the `Makefile`

Hidden config:
* `THREADS` Number of jobs to run simultaneously _(make -j)_ (Default: 1)
* `NICE_OUTPUT` (bool) Show only current compilation (Default: 1)
* `LD_CC` Compiler used to link the executable (Default: compiler used to build objs)
* `LIBS` Makefiles directories to call before the `$(NAME)` rule

_Make sure the Makefile is ready after changing some configs_
