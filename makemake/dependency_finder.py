# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    dependency_finder.py                               :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 17:07:20 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/07 00:14:29 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config
import os
import module
import utils

#
# Find dependencies for a file
#
def track_file(file_name, include_map, module_dirs, included_dirs, include_stack):
	dependencies = []
	include_stack.append(file_name)
	for inc in include_map[file_name]:
		ok = False
		for module, inc_dir in module_dirs:
			abs_header = os.path.abspath(os.path.join(inc_dir, inc))
			if os.path.isfile(abs_header):
				ok = True
				dependencies.append(abs_header)
				included_dirs.append(inc_dir)
				if not abs_header in module.include_map():
					utils.warn("Unknown file '%s' of module %s (included from '%s')" % (abs_header, module.name, file_name))
					break
				if abs_header in include_stack:
					raise config.BaseError("File include loop ('%s' included by '%s')" % (
						os.path.relpath(abs_header), " --> ".join([os.path.relpath(i) for i in include_stack])))
				for dep in track_file(abs_header, module.include_map(), module_dirs, included_dirs, include_stack):
					if not dep in dependencies:
						dependencies.append(dep)
				break
		if not ok:
			raise config.BaseError("Cannot found %s" % inc)
	include_stack.pop()
	return dependencies

#
# Build dependencies for all files of a module
#
def track_module(module):
	dependency_map = {}
	dirs = module.included_dirs()
	included_dirs = []
	for source, ext in module.source_files():
		dependency_map[source] = (track_file(source, module.include_map(), dirs, included_dirs, []), ext)
	for dep in module.private_required:
		ok = False
		for d in dep.public_includes:
			if d in included_dirs:
				ok = True
				break
		if not ok:
			utils.warn("Module %s: Useless dependency '%s'" % (module.name, dep.name))
	included_dirs = []
	for header, ext in module.header_files():
		dependency_map[header] = (track_file(header, module.include_map(), dirs, included_dirs, []), ext)
	for dep in module.public_required:
		ok = False
		for d in dep.public_includes:
			if d in included_dirs:
				ok = True
				break
		if not ok:
			utils.warn("Module %s: Dependency '%s' should be private" % (module.name, dep.name))
	return dependency_map

#
# Call track_module for each module and return a map {module: ({file_name: [dependencies]}, ext_data)}
#
def track(modules):
	m_dependency_map = {}
	for m in modules:
		try:
			m_dependency_map[m] = track_module(m)
		except config.BaseError as e:
			raise config.BaseError("Module %s: %s" % (m.name, str(e)))
	return m_dependency_map
