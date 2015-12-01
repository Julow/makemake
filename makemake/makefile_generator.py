# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    makefile_generator.py                              :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/31 21:26:47 by juloo             #+#    #+#              #
#    Updated: 2015/12/01 23:57:03 by juloo            ###   ########.fr        #
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

# Objects directory
O_DIR			:= _objs

# Jobs
JOBS			:= 4

# Column output
COLUMN_OUTPUT	?= 1
_COLUMN_OUTPUT	:= 0


ifeq ($(COLUMN_OUTPUT),0)
	PRINT_OK	= printf '\\033[32m$<\\033[0m\\n'
	PRINT_LINK	= printf '\\033[32m$@\\033[0m\\n'
else
	PRINT_OK	= (LINE_LENGTH=$$((`cat $(PRINT_FILE) 2>/dev/null`+0));		\\
		if [ $$LINE_LENGTH -ge 0 ]; then									\\
		if [ $$LINE_LENGTH -ge $(PER_LINE) ]; then LINE_LENGTH=0; echo; fi; \\
		echo $$(($$LINE_LENGTH + 1)) > $(PRINT_FILE);						\\
		printf "\\033[32m%%-$(MAX_LEN)s\\033[0m " "$<";						\\
		fi) || (echo "-1" > $(PRINT_FILE) && false)
	PRINT_LINK	= printf '\\n\\033[32m$@\\033[0m\\n'
endif

# Depend file name
DEPEND			:= %(depend_file)s

# tmp
SUBMODULE_RULES	:= $(addsuffix /.git,$(SUBMODULES))
PRINT_FILE		:= .tmp_print

# Default rule (need to be before any include)
all: $(SUBMODULE_RULES) init
ifneq ($(COLUMN_OUTPUT),0)
	-echo "0" > $(PRINT_FILE)
endif
	-make -j$(JOBS) _COLUMN_OUTPUT=$(COLUMN_OUTPUT) $(NAME)
ifneq ($(COLUMN_OUTPUT),0)
	-rm -f $(PRINT_FILE)
endif

# Include $(O_FILES) and dependencies
include $(DEPEND)

# Compute column width
ifneq ($(_COLUMN_OUTPUT),0)
	MAX_LEN		:= $(shell \\
		MAX_LEN=0; for f in $(patsubst $(O_DIR)/%%,%%,$(O_FILES)); do		\\
			if [ $${\\#f} -gt $$MAX_LEN ]; then MAX_LEN=$${\\#f}; fi;		\\
		done; echo $$(($$MAX_LEN + 2))									\\
	)
	PER_LINE	:= $(shell echo $$((`tput cols` / $(MAX_LEN))))
endif

init: $(LIBS_RULES) $(OBJ_DIR_TREE) $(PUBLIC_LINKS)

# Linking
$(NAME): $(LINK_DEPENDS) $(O_FILES)
	clang -o $@ $(O_FILES) $(LINK_FLAGS) && $(PRINT_LINK)

# Compiling
$(O_DIR)/%%.o: %%.c
	clang $(C_FLAGS) -c $< -o $@ && $(PRINT_OK)
$(O_DIR)/%%.o: %%.cpp
	clang++ $(CPP_FLAGS) -c $< -o $@ && $(PRINT_OK)

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
	-rm -f $(PRINT_FILE) 2> /dev/null
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
.PHONY: all clean fclean re debug rebug _debug init
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
