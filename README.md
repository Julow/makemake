# Makemake2

Help to split a program by `module`
(see [module language](#module-language) below)<br />
And generate/_maintains_ a `depend.mk` file

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

	# Add a target-only variable
	local DEBUG_FLAGS += -DDEBUG

	# Disable automatic search of source files
	disable auto

	# Will add 'include <path>/file.mk' to the depend.mk
	makefile include file.mk
	# file.mk will be copied into the depend.mk
	makefile import file.mk

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
module libft: libft/srcs
	public include libft/include
	private include libft/internal/include

module get_next_line: libft/get_next_line/
	public include include/
	public require libft

module math: srcs/math
	public include srcs/math/include
	private require libft

	put LINK_FLAGS -lm

module useless: srcs/useless
	private require libft

# If a main module is declared, unused modules will be discarded
main module test: srcs/test

	private require libft
	private require get_next_line
	private require math
```

Bigger example: [scop](https://github.com/Julow/scop)
