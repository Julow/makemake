# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_searcher.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 08:53:46 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/15 10:09:28 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import module_parser, module_checker

MODULE_FILE_NAME = "module"

EXCLUDE_DIRS = [".git"]

#
# Walk current directory
#  and return a list of 'MODULE_FILE_NAME' file
#

def search():
	module_files = []
	for curr_dir, dirs, ls in os.walk("."):
		if os.path.basename(curr_dir) in EXCLUDE_DIRS:
			del dirs[:]
		else:
			for file_name in ls:
				if file_name == MODULE_FILE_NAME:
					module_files.append(os.path.join(curr_dir, file_name))
	return module_files

#
# search + module_parser.parse + module_checker.check
#

def load():
	modules = []
	for module_file in search():
		modules += module_parser.parse(module_file)
	module_checker.check(modules)
	return modules
