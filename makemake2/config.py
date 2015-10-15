# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    config.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 10:39:40 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/15 13:26:33 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

MODULE_FILE_NAME = "module"

EXCLUDE_DIRS = [".git"]

DEFAULT_VISIBILITY = "private"

SOURCE_EXT = [".c", ".cpp", ".h", ".hpp", ".tpp"]

INCLUDE_REG = '^ *# *include *(?:"([^"]+)"|<([^>]+)>)'

class BaseError(Exception):

	def __init__(self, err):
		self.err = err

	def __str__(self):
		return self.err
