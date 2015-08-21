#!/usr/bin/python
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    makemake.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/08/21 19:45:08 by juloo             #+#    #+#              #
#    Updated: 2015/08/21 21:03:47 by juloo            ###   ########.fr        #
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

# Objects directory
O_DIR := o

# depend file name
DEPEND := .depend

# tmp
MODULE_RULES := $(addsuffix /.git,$(MODULES))

all: $(NAME)

# Include $(O_FILES) and dependencies
include $(DEPEND)

$(NAME): $(MODULE_RULES) $(LIBS) $(O_FILES)
	@echo done

$(O_DIR)/%%.o:
	echo Compiling $< to $@

$(MODULE_RULES):
	git submodule init $(@:.git=)
	git submodule update $(@:.git=)

$(LIBS):
	make -C $@

clean:
	echo clean

fclean: clean
	echo fclean

re: fclean all

$(DEPEND): Makefile
	echo need to do makemake

make:
	echo need to do makemake

.SILENT:
.PHONY: all $(LIBS) clean fclean re make
"""

DEPEND_RULE = """
%(o_file)s: %(includes)s | %(o_dir)s
"""

from os import path
import re, os

source_include_reg = re.compile('^\s*#\s*include\s*"([^"]+)"\s*$')
makefile_var_reg = re.compile('^\s*([a-zA-Z0-9_]+)\s*[:\?\+]?=\s*(.*)$')

#
# Return all files in 'dir_name' recursively
# (except dir starting with '.')
#
def get_file_tree(dir_name):
	tree = []
	for curr_dir, dirs, files in os.walk(dir_name):
		if path.basename(curr_dir).startswith('.'):
			del dirs[:]
		else:
			for f in files:
				tree.append(path.join(curr_dir, f))
	return tree

#
# Create Makefile
# (if it does not exists)
#

def check_makefile(name):
	if not path.isfile(name):
		with open(name, 'w') as f:
			f.write(DEFAULT_MAKEFILE % {
				'name': "",
				'dirs': "",
				'modules': "",
				'libs': ""
			})
			print "Generated %s" % name

#
# Fetch config from the Makefile
#

def fetch_config(name):
	config = {}
	with open(name) as f:
		for line in f:
			m = makefile_var_reg.match(line)
			if m != None:
				config[m.group(1)] = m.group(2)
	return config

#
# Generate $(DEPEND) file
#

def get_source_files(file_tree):
	source_files = []
	for f in file_tree:
		if f.endswith('.c'): # TODO
			source_files.append(f)
	return source_files

def get_include_files(file_tree, base_dir):
	include_files = {}
	for f in file_tree:
		include_files[path.relpath(f, base_dir)] = f
	return include_files

def get_includes(source, include_files):
	includes = [source]
	with open(source) as f:
		for line in f:
			m = source_include_reg.match(line)
			if m != None and m.group(1) in include_files:
				includes += get_includes(include_files[m.group(1)], include_files)
	return includes

def generate_depend(name, dirs, o_dir):
	source_files = []
	include_files = {} # 'include name': 'file path'
	obj_files = {} # 'obj_name': ['includes']
	for d in dirs:
		f_tree = get_file_tree(d)
		source_files += get_source_files(f_tree)
		include_files.update(get_include_files(f_tree, d))
	for source in source_files:
		obj = path.join(o_dir, source.replace('.c', '.o')) # TODO
		obj_files[obj] = get_includes(source, include_files)
	with open(name, 'w') as f:
		f.write("O_FILES := \\\n")
		for obj in obj_files:
			f.write("	%s \\\n" % obj)
		f.write("\n")
		for obj in obj_files:
			f.write(DEPEND_RULE % {
				'o_file': obj,
				'includes': " ".join(obj_files[obj]),
				'o_dir': path.dirname(source)
			})
		print "Generated %s" % name

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
config = None
try:
	config = fetch_config(MAKEFILE_NAME)
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
	generate_depend(config['DEPEND'], config['DIRS'].split(), config['O_DIR'])
except Exception as e:
	print "Error Cannot generate %s: %s" % (config['DEPEND'], e)
	exit(1)
