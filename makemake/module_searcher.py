# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_searcher.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 08:53:46 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/05 18:46:08 by jaguillo         ###   ########.fr        #
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
# Change strings in public_required and private_required
#  to reference to corresponding Module
#
# TODO: handle this in parser

def resolve_refs(module_list):
	name_map = {}
	for m in module_list:
		name_map[m.name] = m
	for m in module_list:
		def resolve_list(l):
			resolved = []
			for r in l:
				if not r in name_map:
					raise config.BaseError("Unknown module '%s' (required by %s)" % (r, m.name)) # TODO: exception
				resolved.append(name_map[r])
			return resolved
		m.public_required = resolve_list(m.public_required)
		m.private_required = resolve_list(m.private_required)

#
# search + module_parser.parse + resolve_refs
#

def parse_all():
	modules = []
	for module_file in search():
		modules += module_parser.parse(module_file)
	resolve_refs(modules)
	return modules

#
# Return a copy of the list 'modules' without unused modules
#

def filter_unused(modules):
	used_map = {}
	def check_used(m):
		if not m.name in used_map:
			used_map[m.name] = m
			for dep in m.public_required:
				check_used(dep)
			for dep in m.private_required:
				check_used(dep)
	for m in modules:
		if m.is_main:
			check_used(m)
	return used_map.values()

#
# search + module_parser.parse + resolve_refs + filter_unused + module_checker.check
#

def load():
	modules = parse_all()
	modules = filter_unused(modules)
	module_checker.check(modules)
	return modules
