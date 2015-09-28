#!/usr/bin/python
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    makemake.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/08/21 19:45:08 by juloo             #+#    #+#              #
#    Updated: 2015/09/29 01:41:11 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#
# Makemake
#
# Usage:
#   makemake
#   (no arg needed)
#
# Create a Makefile (only if it does not already exists)
# Generate a $(DEPEND) file (or update it)
#

MAKEFILE_NAME = "Makefile"

MAX_LINE_LENGTH = 80

SUB_MAKEFILE_NAMES = ["Makefile"]

EXCLUDE_DIRS = [".git"]

EXTENSIONS = [
	{"ext": ".c",	"obj_ext": ".o"},
	{"ext": ".cpp",	"obj_ext": ".o"}
]

O_FILES_VAR = "O_FILES :=\t"
DEPEND_RULE = "%s:"

LIBS_DEPEND_VAR = "LIBS_DEPEND := "

DEFAULT_MAKEFILE = """#

# Executable name
NAME := %(name)s

# Project directories
DIRS := %(dirs)s

# Git submodule to init
MODULES := %(modules)s
# Makefiles to call
LIBS := %(libs)s

# Compilation and linking flags
FLAGS := -Wall -Wextra -O2
# Compilation flags
HEADS := $(addprefix -I,$(DIRS))
# Linking flags
LINKS :=

# Objects directory
O_DIR := o

# Depend file name
DEPEND := depend.mk

# tmp
MODULE_RULES := $(addsuffix /.git,$(MODULES))

# Default rule (need to be before any include)
all: $(MODULE_RULES) libs $(NAME)

# Include $(O_FILES) and dependencies
-include $(DEPEND)

# Linking
$(NAME): $(LIBS_DEPEND) $(O_FILES)
	clang $(FLAGS) -o $@ $(O_FILES) $(LINKS) && printf '\\033[32m$@\\033[0m\\n'

# Compiling
$(O_DIR)/%%.o:
	clang $(FLAGS) $(HEADS) -c $< -o $@ && printf '\\033[32m$<\\033[0m\\n'

# Init submodules
$(MODULE_RULES):
	git submodule init $(@:.git=)
	git submodule update $(@:.git=)

# Create obj directories
$(O_DIR)/%%/:
	mkdir -p $@

# Set debug mode and make
debug: _debug all

# Clean, set debug mode and make
rebug: fclean debug

# Clean obj files
clean:
	rm -f $(O_FILES)

# Clean everything
fclean: clean
	rm -f $(NAME)

# Clean and make
re: fclean all

# Update $(DEPEND) file
$(DEPEND): Makefile
	makemake || printf "\\033[31mCannot remake $(DEPEND)\\033[0m\\n"

# Set debug flags
_debug:
	$(eval FLAGS := $(DEBUG_FLAGS))

.SILENT:
.PHONY: all $(LIBS) clean fclean re debug rebug _debug
"""

import re, os
from os import path

source_include_reg = re.compile('^\s*#\s*include\s*"([^"]+)"\s*$')
makefile_var_reg = re.compile('^\s*([a-zA-Z0-9_]+)\s*[:\?\+]?=\s*(.*)$')
module_path_reg = re.compile('^\s*path\s*=\s*(.+)$')

# Return all files in 'dir_name' recursively
# (except dir starting with '.')
def get_file_tree(dir_name):
	tree = []
	for curr_dir, dirs, files in os.walk(dir_name):
		if path.basename(curr_dir) in EXCLUDE_DIRS:
			del dirs[:]
		else:
			for f in files:
				tree.append(path.join(curr_dir, f))
	return tree

# Return True if what startswith any string of lst
def any_startswith(lst, what):
	for s in lst:
		if what.startswith(s):
			return True
	return False

#
# Create Makefile
# (if it does not exists)
#

# Guess project name
def guess_name():
	return path.basename(os.getcwd())

# Guess project dirs
def guess_dirs_for(file_tree, libs, ext):
	dirs = []
	for f in file_tree:
		if f.endswith(ext):
			if not any_startswith(dirs, f) and not any_startswith(libs, f):
				dirs.append(path.dirname(f))
	return dirs

def guess_dirs(file_tree, libs):
	return guess_dirs_for(file_tree, libs, '.c') + guess_dirs_for(file_tree, libs, '.h')

# Guess sub modules
def guess_modules():
	try:
		with open('.gitmodules') as f:
			modules = []
			for line in f:
				m = module_path_reg.match(line)
				if m != None:
					modules.append(m.group(1))
			return modules
	except:
		return []

# Guess sub Makefiles
def guess_libs(file_tree):
	libs = []
	for f in file_tree:
		if path.basename(f) in SUB_MAKEFILE_NAMES and not any_startswith(libs, f):
			libs.append(path.dirname(f))
	return libs

# Return file_tree starting at the current childs
def get_sub_file_tree():
	for _, sub_dirs, _ in os.walk('.'):
		files = []
		for sub_d in sub_dirs:
			if not sub_d in EXCLUDE_DIRS:
				files += get_file_tree(sub_d)
		return files

#
def check_makefile(name):
	if not path.isfile(name):
		file_tree = get_sub_file_tree()
		libs = guess_libs(file_tree)
		with open(name, 'w') as f:
			f.write(DEFAULT_MAKEFILE % {
				'name': guess_name(),
				'dirs': " ".join(guess_dirs(file_tree, libs)),
				'modules': " ".join(guess_modules()),
				'libs': " ".join(libs)
			})

#
# Generate $(DEPEND) file
#

# Return true if f ends with a supported extension
def is_supported_extension(f):
	for e in EXTENSIONS:
		if f.endswith(e["ext"]):
			return True
	return False

# Return obj of a file replacing it's extension
def get_obj_ext(f):
	for e in EXTENSIONS:
		if f.endswith(e["ext"]):
			return f[:-len(e["ext"])] + e["obj_ext"]
	return None

# Filter file_tree and return a list of source files
def get_source_files(file_tree):
	source_files = []
	for f in file_tree:
		if is_supported_extension(f):
			source_files.append(f)
	return source_files

# Return a map {'include name': 'file path'} of include files
def get_include_files(file_tree, base_dir):
	include_files = {}
	for f in file_tree:
		include_files[path.relpath(f, base_dir)] = f
	return include_files

# Recursively search for #include
def get_includes(source, include_files):
	includes = [source]
	with open(source) as f:
		for line in f:
			m = source_include_reg.match(line)
			if m != None and m.group(1) in include_files:
				for i in sorted(get_includes(include_files[m.group(1)], include_files)):
					if not i in includes:
						includes.append(i)
	return includes

# Return a map {'obj name': ['includes']} of objects files with their includes
def get_obj_files(source_files, include_files, o_dir):
	obj_files = {}
	for source in source_files:
		obj = path.join(o_dir, get_obj_ext(source))
		obj_files[obj] = get_includes(source, include_files)
	return obj_files

# Return a tuple (['libs depends'], ['libs'])
def get_libs_depend(libs_def):
	libs = []
	libs_depend = []
	for d in libs_def:
		libs.append(d)
		try:
			with open("%s/Makefile" % d) as f:
				for line in f:
					m = makefile_var_reg.match(line)
					if m != None and m.group(1) == "NAME":
						libs_depend.append("%s/%s" % (d, m.group(2)))
						break
		except:
			pass
	return (libs_depend, libs)

# Print a list of file respecting MAX_LINE_LENGTH
def print_file_list(out, files, offset, indent, sep, endl):
	indent_len = len(indent.expandtabs(4))
	sep_len = len(sep)
	endl_len = len(endl)
	for f in files:
		if (len(f) + offset + sep_len + endl_len) > MAX_LINE_LENGTH and offset != indent_len:
			offset = indent_len
			out.write(endl)
			out.write("\n")
			out.write(indent)
		if offset > indent_len:
			out.write(sep)
			offset += sep_len
		out.write(f)
		offset += len(f)
	return offset

#
def generate_depend(name, dirs, o_dir, libs_def):
	source_files = []
	include_files = {}
	for d in dirs:
		f_tree = get_file_tree(d)
		source_files += get_source_files(f_tree)
		include_files.update(get_include_files(f_tree, d))
	obj_files = get_obj_files(source_files, include_files, o_dir)
	libs_depend, libs = get_libs_depend(libs_def)
	with open(name, 'w') as f:
		# obj files
		f.write(O_FILES_VAR)
		obj_file_names = sorted(obj_files.keys())
		print_file_list(f, obj_file_names, len(O_FILES_VAR), "\t\t\t", " ", " \\")
		f.write("\n\n")
		# libs depend and libs rule
		f.write(LIBS_DEPEND_VAR)
		print_file_list(f, libs_depend, len(LIBS_DEPEND_VAR), "\t\t\t\t", " ", " \\")
		f.write("\n\nlibs:\n")
		for l in libs:
			f.write("\tmake -C %s\n" % l)
		f.write(".PHONY: libs\n\n")
		# obj depends
		for obj_name in obj_file_names:
			rule_name = DEPEND_RULE % obj_name
			f.write(rule_name)
			offset = print_file_list(f, obj_files[obj_name], len(rule_name), "\t", " ", " \\")
			o_dir_dep = "| %s/" % path.dirname(obj_name)
			if (len(o_dir_dep) + 1 + offset) > MAX_LINE_LENGTH:
				f.write(" \\\n\t%s\n" % o_dir_dep)
			else:
				f.write(" %s\n" % o_dir_dep)

#
# Main
#

# check for makefile or create it
try:
	check_makefile(MAKEFILE_NAME)
except Exception as e:
	print "Error: Cannot create %s: %s" % (MAKEFILE_NAME, e)
	exit(1)

# fetch vars
config = {}
try:
	with open(MAKEFILE_NAME) as f:
		for line in f:
			m = makefile_var_reg.match(line)
			if m != None:
				config[m.group(1)] = m.group(2)
except Exception as e:
	print "Error: Cannot fetch config: %s" % e
	exit(1)

# test required vars
for var in ['DEPEND', 'DIRS', 'O_DIR']:
	if config is None or var not in config:
		print "Error: Variable $(%s) not present in %s" % (var, MAKEFILE_NAME)
		exit(1)
	elif len(config[var]) <= 0:
		print "Error: Variable $(%s) incomplete in %s" % (var, MAKEFILE_NAME)
		exit(1)

# generate $(DEPEND)
try:
	libs = config['LIBS'].split() if 'LIBS' in config else []
	generate_depend(config['DEPEND'], config['DIRS'].split(), config['O_DIR'], libs)
except Exception as e:
	print "Error Cannot generate %s: %s" % (config['DEPEND'], e)
	exit(1)
