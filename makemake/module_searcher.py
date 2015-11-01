# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_searcher.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 08:53:46 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/01 15:29:14 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import module_parser
import module_checker
import config

#
# Walk current directory
#  and return a list of 'MODULE_FILE_NAME' file
#

def search():
	module_files = []
	for curr_dir, dirs, ls in os.walk("."):
		if os.path.basename(curr_dir) in config.EXCLUDE_DIRS:
			del dirs[:]
		else:
			for file_name in ls:
				if file_name == config.MODULE_FILE_NAME:
					module_files.append(os.path.join(curr_dir, file_name))
	return module_files

#
# search + module_parser.parse
#

def all():
	modules = []
	for module_file in search():
		modules += module_parser.parse(module_file)
	return modules

#
# Change strings in public_required and private_required
#  to reference to corresponding Module
#
# TODO: handle this in parser

def resolve_refs(module_list):
	name_map = {}
	for m in module_list:
		name_map[m.name] = m
	def resolve_list(l):
		resolved = []
		for r in l:
			if not r in name_map:
				raise config.BaseError("Unknown module '%s'" % r) # TODO: exception
			resolved.append(name_map[r])
		return resolved
	for m in module_list:
		m.public_required = resolve_list(m.public_required)
		m.private_required = resolve_list(m.private_required)

#
# search + module_parser.parse + resolve_refs + module_checker.check
#

def load():
	modules = all()
	resolve_refs(modules)
	module_checker.check(modules)
	return modules