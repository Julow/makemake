# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    makefile_generator.py                              :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/31 21:26:47 by juloo             #+#    #+#              #
#    Updated: 2016/02/09 13:48:52 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config
import os
import re

MAKEFILE = """
#

# Executable name
NAME			:= %(name)s

# Git submodule to init
SUBMODULES		:= %(submodules)s

# Base flags
BASE_FLAGS		= -Wall -Wextra
%(include_flags)s	=

# Compilation flags (per language)
C_FLAGS			= $(%(include_flags)s) $(BASE_FLAGS)
CPP_FLAGS		= $(%(include_flags)s) $(BASE_FLAGS) -std=c++14

LINK_FLAGS		= $(BASE_FLAGS)

DEBUG_MODE		?= 0
ifeq ($(DEBUG_MODE),1)
	# Extra flags used in debug mode
	BASE_FLAGS	+= -g
else
	# Extra flags used when not in debug mode
	BASE_FLAGS	+= -O2
endif
export DEBUG_MODE

# Compilers
CC				= clang
CXX				= clang++
LINKER			= $(CC)

# Objects directory
O_DIR			:= _objs

# Jobs
JOBS			:= 4

# Depend file name
DEPEND			:= %(depend_file)s

# tmp
SUBMODULE_RULES	:= $(addsuffix /.git,$(SUBMODULES))
PRINT_OK		= printf '\\033[32m$<\\033[0m\\n'
PRINT_LINK		= printf '\\033[32m$@\\033[0m\\n'

# Default rule (need to be before any include)
all: init
	make -j$(JOBS) $(NAME)

# Include $(O_FILES) and dependencies
include $(DEPEND)

# make -n
n: init
	make -n $(NAME)

init: $(SUBMODULE_RULES) $(LIBS_RULES) $(OBJ_DIR_TREE) $(PUBLIC_LINKS)

# Linking
$(NAME): $(OBJ_DIR_TREE) $(PUBLIC_LINKS) $(LINK_DEPENDS) $(O_FILES)
	$(LINKER) -o $@ $(O_FILES) $(LINK_FLAGS) && $(PRINT_LINK)

# Compiling
$(O_DIR)/%%.o: %%.c
	$(CC) $(C_FLAGS) -c $< -o $@ && $(PRINT_OK)
$(O_DIR)/%%.o: %%.cpp
	$(CXX) $(CPP_FLAGS) -c $< -o $@ && $(PRINT_OK)
	$(eval LINKER = $(CXX))

# Init submodules
$(SUBMODULE_RULES):
	git submodule init $(@:.git=)
	git submodule update $(@:.git=)

# Create include links
$(PUBLIC_LINKS):
	ln -fs $(abspath $<) $@
# Create obj directories
$(OBJ_DIR_TREE):
	mkdir -p $@

# Set debug mode and make
debug: _debug all

# Clean, set debug mode and make
rebug: fclean debug

# Clean obj files
clean:
	-rm -f $(O_FILES) $(PUBLIC_LINKS) 2> /dev/null
	-rm -df $(OBJ_DIR_TREE) 2> /dev/null

# Clean everything
fclean: clean
	rm -f $(NAME)

# Clean and make
re: fclean all

# Set debug flags
_debug:
	$(eval DEBUG_MODE = 1)

.SILENT:
.PHONY: all n clean fclean re debug rebug _debug init
"""

# Guess project name
def guess_name():
	return os.path.basename(os.getcwd())

# Guess sub modules
def guess_submodules():
	try:
		with open('.gitmodules') as f:
			modules = []
			for line in f:
				m = config.GIT_SUBMODULE_REG.match(line)
				if m != None:
					modules.append(m.group(1))
			return modules
	except:
		return []

# Overwrite 'file_name' with a fresh default Makefile
def gen(file_name):
	with open(file_name, "w") as f:
		f.write(MAKEFILE % {
			"name": guess_name(),
			"submodules": " ".join(guess_submodules()),
			"include_flags": config.INCLUDE_FLAGS_VAR,
			"depend_file": config.DEPEND_FILE_NAME
		})
