# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    config.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 10:39:40 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/31 23:12:24 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

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

MAX_LINE_LENGTH = 80

INCLUDE_FLAGS_VAR = "INCLUDE_FLAGS"

INCLUDE_REG = '^ *# *include *(?:"([^"]+)"|<([^>]+)>)'
GIT_SUBMODULE_REG = '^\s*path\s*=\s*(.+)$'

class BaseError(Exception):

	def __init__(self, err):
		self.err = err

	def __str__(self):
		return self.err
