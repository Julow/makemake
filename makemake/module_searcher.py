# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_searcher.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 08:53:46 by jaguillo          #+#    #+#              #
#    Updated: 2017/02/27 18:41:35 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import module_parser
import config
import utils

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

def filter_unused(modules, mains):
	used_map = {}
	def check_used(m):
		if not m.name in used_map:
			used_map[m.name] = m
			for dep in m.public_required:
				check_used(dep)
			for dep in m.private_required:
				check_used(dep)
	ok = False
	for m in mains:
		ok = True
		check_used(m)
	if not ok:
		return modules
	return used_map.values()

#
# 'main_names' is the list of the main modules to use
# If 'main_names' is empty, use all the main modules
# Return (the list of modules, main modules)
#

def filter_mains(modules, main_names):
	main_map = {m.name: m for m in modules if m.is_main}
	def main_by_names():
		mains = []
		for name in main_names:
			if name not in main_map:
				utils.warn("Unknown main module '%s'" % name)
				continue
			if main_map[name] == None:
				utils.warn("Main module '%s' specified twice" % name)
				continue
			mains.append(main_map[name])
			main_map[name] = None
		return mains
	mains = main_by_names() if len(main_names) > 0 else main_map.values()
	return (filter_unused(modules, mains), mains)
