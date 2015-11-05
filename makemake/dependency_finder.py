# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    dependency_finder.py                               :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 17:07:20 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/05 20:13:36 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config
import re
import os
import source_finder
import module
import utils

INCLUDE_REG = re.compile(config.INCLUDE_REG)

#
# Class used to build a list of dependency
#

class DependencyMap():

	def __init__(self):

		self.track_map = {}
		self.search_dirs = []

	def track(self, file_name, track_stack, included_dirs = None):
		if file_name in self.track_map:
			if self.track_map[file_name] == None:
				raise config.BaseError("Include loop") # TODO: exception
			return self.track_map[file_name]
		track_stack.append(file_name)
		self.track_map[file_name] = None
		includes = []
		for inc in scan(file_name):
			ok = False
			for d in self.search_dirs:
				inc_abs = os.path.join(d, inc)
				if os.path.isfile(inc_abs):
					if included_dirs != None:
						included_dirs.append(d)
					includes.append(inc_abs)
					for i in self.track(inc_abs, track_stack):
						if not i in includes:
							includes.append(i)
					ok = True
					break
			 # TODO: relative include
			 # or TODO: soft error
			if not ok:
				raise config.BaseError("Cannot find '%s' included from module %s" % (
					inc, " -> ".join([os.path.relpath(i) for i in track_stack])
				)) # TODO: exception
		self.track_map[file_name] = includes
		track_stack.pop()
		return includes

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
	dirs = list(module.public_includes)
	module_list = list(module_list)
	module_list.remove(module)
	for r in module.public_required:
		for d in get_dirs(module_list, r, False):
			if not d in dirs:
				dirs.append(d)
	if private:
		dirs += module.private_includes
		for r in module.private_required:
			for d in get_dirs(module_list, r, False):
				if not d in dirs:
					dirs.append(d)
	return dirs

#
# Search source files and their dependencies
#  return a map {source_name: (dependencies, ext data)}
#

def track_dir(module, public_includes, dep = None, included_dir = None):
	sources = {}
	if dep == None:
		dep = DependencyMap()
	dep.search_dirs = public_includes
	for (f, ext_data) in source_finder.find(module.base_dir):
		sources[f] = (dep.track(os.path.abspath(f), [module.name], included_dir), ext_data)
	return sources

#
# It's like using track_dir and get_dirs together
#  return a map {module: track_dir()}
#

def track(modules):
	source_map = {}
	dep_map = DependencyMap()
	for m in modules:
		if not m.auto_enabled:
			source_map[m] = {}
			continue
		included_dir = []
		source_map[m] = track_dir(m, get_dirs(modules, m), dep_map, included_dir)
		def check_useless_dep(lst):
			for dep in lst:
				ok = False
				for d in dep.public_includes:
					if d in included_dir:
						ok = True
						break
				if not ok:
					utils.warn("Module %s: Useless dependency '%s'" % (m.name, dep.name))
		check_useless_dep(m.public_required)
		check_useless_dep(m.private_required)
	return source_map

#
