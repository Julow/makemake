# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    config.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 10:39:40 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/02 22:54:21 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import makemake
import os

MODULE_FILE_NAME = "module"

EXCLUDE_DIRS = [".git"]

DEFAULT_VISIBILITY = "private"

EXTENSIONS = [
	{"ext": ".c",	"obj_ext": ".o", "is_source": True},
	{"ext": ".cpp",	"obj_ext": ".o", "is_source": True},
	{"ext": ".h",	"is_source": False},
	{"ext": ".hpp",	"is_source": False},
	{"ext": ".tpp",	"is_source": False},
]

OBJ_DIR = "$(O_DIR)"

MAKEFILE_NAME = "Makefile"
DEPEND_FILE_NAME = "depend.mk"

MAX_LINE_LENGTH = 80

INCLUDE_FLAGS_VAR = "INCLUDE_FLAGS"

INCLUDE_REG = '^ *# *include *(?:"([^"]+)"|<([^>]+)>)'
GIT_SUBMODULE_REG = '^\s*path\s*=\s*(.+)$'

# Open (read only) a data file
def get_file(file_name):
	return open(os.path.join(makemake.__path__[0], file_name), "r")

# Concat the content of a data file in a string
def cat_file(file_name):
	with get_file(file_name) as f:
		return f.read()

# Base exception for . error
class BaseError(Exception):

	def __init__(self, err):
		self.err = err

	def __str__(self):
		return self.err
