# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    config.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 10:39:40 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/17 12:50:42 by jaguillo         ###   ########.fr        #
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

PUBLIC_LINK_DIR = "_public"

MAKEFILE_NAME = "Makefile"
DEPEND_FILE_NAME = "depend.mk"

MAX_LINE_LENGTH = 80

INCLUDE_FLAGS_VAR = "INCLUDE_FLAGS"

INCLUDE_REG = '^ *# *include *"([^/]+)/([^"]+)"'
GIT_SUBMODULE_REG = '^\s*path\s*=\s*(.+)$'
VARIABLE_REG = '\?([a-zA-Z0-9_]+)\?'

# Base exception for . error
class BaseError(Exception):

	def __init__(self, err):
		self.err = err

	def __str__(self):
		return self.err
