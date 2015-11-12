# Makemake2

Help to split a program by `module`
(see [module language](#module-language) below)<br />
And generate/_maintains_ a `depend.mk` file (see [below](#generated-depend-mk))

### Usage

- `makemake2 check` Search modules and check for error/warning
- `makemake2 gen` Generate depend file
- `makemake2 info` Show info about modules, puts, dependencies...
- `makemake2 list` Search and list all modules
- `makemake2 makefile` Generate a basic Makefile
- `makemake2 print` Open a web browser and draw the module tree

For more help: `makemake2 help`

### Get it

Using brew: _([brew tap](https://github.com/Julow/homebrew-tap))_<br />
`brew install Julow/tap/makemake`;

Without brew: Clone _(or download)_ and run<br />
`sudo python setup.py install`

### Module language

```makefile
# Declare a new module
module <module_name>: <module_dir>
	# module_dir is optional (default: ./)
	# module_name can use any char (except whitespace)

	# Location of public headers
	public include <public_headers_dir>

	# Location of private headers
	private include <private_headers_dir>
	# Support several include declarations (public or private)

	# Require an other module (publicly)
	public require <dependency>
	# Same but privately
	private require <dependency2>

	# Put (without dupplicate) a word in a variable
	put LINK_FLAGS -lm

	# ?path? is substitued with the module's (relative) base_dir
	put CONFIG_FILES ?path?/config_file
	# ?name? is substitued with the module's name
	put MODULE_NAMES ?name?

	# Add a target-only variable
	local DEBUG_FLAGS += -DDEBUG

	# Add a source directory (relative to <module_dir>)
	source srcs/
	# If no source directory are specified, default is './'

	# Disable automatic search of source files
	disable auto

	# Will add 'include <path>/file.mk' to the depend.mk
	makefile include file.mk
	# file.mk will be copied into the depend.mk
	makefile import file.mk
	# imported file have access to ?path? and ?name? substitutions

	# Default visibility (public/private) is private
	# Every declarations are optional
	# Path are relative to the 'module' file location
	# The indentation is not important
```

A module declaration have to be written in a 'module' file

A 'module' file can contains 0 or several declarations
and are searched recursively

##### Example:

```makefile
module libft: libft/
	public include include
	private include internal/include
	source srcs

module get_next_line: libft/get_next_line/
	public include include/
	public require libft

module math: srcs/math
	public include include/
	private require libft

	put LINK_FLAGS -lm

module useless: srcs/useless
	private require libft

# If a main module is declared, unused modules will be discarded
main module test: srcs/test

	private include include/

	local LOL = ?path?

	private require libft
	private require get_next_line
	private require math
```

Bigger example: [scop](https://github.com/Julow/scop)

##### Generated depend.mk

Objects files are put in the `$(O_FILES)` variable

`$(O_DIR)` have to be declared _before_ including `depend.mk`

```makefile
## first the put'd variables (user defined)
LINK_FLAGS += -lm
## O_FILES var
O_FILES += $(O_DIR)/srcs/test/test.o $(O_DIR)/libft/srcs/ft_memcpy.o \
	$(O_DIR)/libft/get_next_line/get_next_line.o
## PUBLIC_DIRS var
PUBLIC_DIRS += libft/include libft/get_next_line/include srcs/math/include

## then dependencies

# module libft
$(O_DIR)/libft/srcs/ft_memcpy.o: INCLUDE_FLAGS += -Ilibft
$(O_DIR)/libft/srcs/ft_memcpy.o: libft/srcs/ft_memcpy.c libft/libft.h

# module get_next_line
$(O_DIR)/libft/get_next_line/get_next_line.o: INCLUDE_FLAGS += -Ilibft \
	-Ilibft/get_next_line
$(O_DIR)/libft/get_next_line/get_next_line.o: \
	libft/get_next_line/get_next_line.c libft/libft.h \
	libft/get_next_line/get_next_line.h

# module test

## if module have "makefile import" or "makefile include"
## it goes here

## local variables
$(O_DIR)/srcs/test/test.o: LOL = srcs/test
## INCLUDE_FLAGS is an automatic local
$(O_DIR)/srcs/test/test.o: INCLUDE_FLAGS += -Ilibft -Ilibft/get_next_line \
	-Isrcs/test/include -Isrcs/math/include
## dependencies
$(O_DIR)/srcs/test/test.o: srcs/test/test.c srcs/test/include/test.h \
	libft/get_next_line/get_next_line.h libft/libft.h
```
