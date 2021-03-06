# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    config.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 10:39:40 by jaguillo          #+#    #+#              #
#    Updated: 2016/05/30 23:38:39 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import re

MODULE_FILE_NAME = "module"

EXCLUDE_DIRS = [".git"]

DEFAULT_VISIBILITY = "private"

NAMESPACES_SEPARATOR = "::"

EXTENSIONS = [
	{"ext": ".c",	"obj_ext": ".o", "is_source": True},
	{"ext": ".cpp",	"obj_ext": ".o", "is_source": True},
	{"ext": ".h",	"is_source": False},
	{"ext": ".hpp",	"is_source": False},
	{"ext": ".tpp",	"is_source": False},
]

OBJ_DIR = "$(O_DIR)"

OBJ_DIR_TREE_VAR = "OBJ_DIR_TREE"
OBJ_FILES_VAR = "O_FILES"

PUBLIC_LINK_DIR = "_public"
PUBLIC_LINKS_VAR = "PUBLIC_LINKS"
PUBLIC_LINK_DIRS = "PUBLIC_LINK_DIRS"

MAINS_VAR = "MAINS"

MAKEFILE_NAME = "Makefile"
DEPEND_FILE_NAME = "depend.mk"

MAX_LINE_LENGTH = 80

INCLUDE_FLAGS_VAR = "INCLUDE_FLAGS"

INCLUDE_REG = re.compile('^ *# *include *"(?:([^/]+)/)?([^"]+)"') # TODO: fix
GIT_SUBMODULE_REG = re.compile('^\s*path\s*=\s*(.+)$')
VARIABLE_REG = re.compile('\?([a-zA-Z0-9_]+)\?')
MODULE_NAME_REG = re.compile('^(?:[a-zA-Z0-9_\.-]|::)+$')

# Base exception for . error
class BaseError(Exception):

	def __init__(self, err):
		self.err = err

	def __str__(self):
		return self.err
