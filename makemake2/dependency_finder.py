# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    dependency_finder.py                               :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 17:07:20 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/15 18:00:55 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config
import re
import os
import source_finder
import module_def

INCLUDE_REG = re.compile(config.INCLUDE_REG)

#
# Return a list of included file
#

def scan(file_name):
	included = []
	with open(file_name, "r") as f:
		for line in f:
			m = INCLUDE_REG.match(line)
			if m != None and m.group(1) != None:
				included.append(m.group(1))
	return included

#
# Look recursively for required modules's include directories
#

def get_dirs(module_list, module, private = True):
	dirs = [module.base_dir] + module.include_dirs
	module_list = list(module_list)
	module_list.remove(module)
	for r in module.public_required:
		for d in get_dirs(module_list, _get_module(module_list, r), False):
			if not d in dirs:
				dirs.append(d)
	if private:
		for r in module.private_required:
			for d in get_dirs(module_list, _get_module(module_list, r), False):
				if not d in dirs:
					dirs.append(d)
	return dirs

#
# Search source files and their dependencies
#  return a map {source_name: dependencies}
#

def track_dir(search_dir, include_dirs):
	dep = DependencyMap(include_dirs)
	for f in source_finder.find(search_dir):
		dep.track(os.path.abspath(f))
	return dep.map

#
# It's like using track_dir and get_dirs together
#  return a map {module: {source_name: dependencies}}
#

def track(modules):
	source_map = {}
	for m in modules:
		if not m.auto_enabled:
			source_map[m] = []
			continue
		source_map[m] = track_dir(m.base_dir, get_dirs(modules, m))
	return source_map

#
#
#

def _get_module(module_list, name):
	m = module_def.get_module(module_list, name)
	if m == None:
		raise config.BaseError("Include loop: '%s' included from ??" % name)
	return m

#

class DependencyMap():

	def __init__(self, search_dirs):

		self.map = {}
		self.search_dirs = search_dirs

	def track(self, file_name):
		if file_name in self.map:
			if self.map[file_name] == None:
				raise config.BaseError("Include loop") # TODO: exception
			return self.map[file_name]
		self.map[file_name] = None
		includes = []
		for inc in scan(file_name):
			ok = False
			for d in self.search_dirs:
				inc_abs = os.path.join(d, inc)
				if os.path.isfile(inc_abs):
					includes.append(inc_abs)
					for i in self.track(inc_abs):
						if not i in includes:
							includes.append(i)
					ok = True
					break
			if not ok: # TODO: relative include
				raise config.BaseError("Unable to found include '%s' included from '%s'" % (
					inc, file_name
				)) # TODO: exception
		self.map[file_name] = includes
		return includes
