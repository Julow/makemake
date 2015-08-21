#!/usr/bin/python
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    makemake.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/08/21 19:45:08 by juloo             #+#    #+#              #
#    Updated: 2015/08/21 19:52:42 by juloo            ###   ########.fr        #
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

DEPEND := .depend

# tmp
MODULE_RULES := $(addsuffix /.git,$(MODULES))

all: $(NAME)

# Include $(O_FILES) and dependencies
include $(DEPEND)

$(NAME): $(MODULE_RULES) $(LIBS) $(O_FILES)
	@echo done

$(O_DIR)/%%.o:
	@echo Compiling $< to $@

$(MODULE_RULES):
	@git submodule init $(@:.git=)
	@git submodule update $(@:.git=)

$(LIBS):
	make -C $@

clean:
	@echo clean

fclean: clean
	@echo fclean

re: fclean all

$(DEPEND): Makefile
	makemake

make:
	makemake

.SILENT:
.PHONY: all $(LIBS) clean fclean re make
"""

from os import path
import re

makefile_var_reg = re.compile('^\s*([a-zA-Z0-9_]+)\s*[:\?\+]?=\s*(.*)$')

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
			print "Generated Makefile"

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

def generate_depend(name, dirs):
	print "Generate .depend not implemented"

#
# Main
#

try:
	check_makefile(MAKEFILE_NAME)
except Exception as e:
	print "Error: Cannot create Makefile: %s" % e
	exit(1)

makefile_vars = None
try:
	makefile_vars = fetch_config(MAKEFILE_NAME)
except Exception as e:
	print "Error: Cannot fetch config: %s" % e
	exit(1)

for var in ['DEPEND', 'DIRS']:
	if makefile_vars is None or var not in makefile_vars:
		print "Error: Variable %s not present" % var
		exit(1)

try:
	generate_depend(makefile_vars['DEPEND'], makefile_vars['DIRS'])
except Exception as e:
	print "Error Cannot generate %s: %s" % (makefile_vars['DEPEND'], e)
	exit(1)

print "done"
