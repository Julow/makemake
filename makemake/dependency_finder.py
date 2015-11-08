# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    dependency_finder.py                               :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 17:07:20 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/07 15:54:55 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config
import os
import utils

#
# Find dependencies for a file
#
# TODO: ordered_set
def track_file(module, file_name, included_dirs, include_stack):
	dependencies = []
	include_stack.append(file_name)
	for inc in module.include_map()[file_name]:
		ok = False
		for m, inc_dir in module.private_dirs():
			abs_header = os.path.abspath(os.path.join(inc_dir, inc))
			if os.path.isfile(abs_header):
				ok = True
				dependencies.append(abs_header)
				included_dirs.add(inc_dir)
				if not abs_header in m.include_map():
					utils.warn("Unknown file '%s' of module %s (included from '%s')" % (abs_header, m.name, file_name))
					break
				if abs_header in include_stack:
					raise config.BaseError("File include loop ('%s' included by '%s')" % (
						os.path.relpath(abs_header), " --> ".join([os.path.relpath(i) for i in include_stack])))
				for dep in track_file(m, abs_header, included_dirs, include_stack):
					if not dep in dependencies:
						dependencies.append(dep)
				break
		if not ok:
			raise config.BaseError("Cannot found '%s' included from '%s'" % (inc, os.path.relpath(file_name)))
	include_stack.pop()
	return dependencies

#
# Build dependencies for all files of a module
#
def track_module(module):
	dependency_map = {}
	included_dirs = set()
	for source, ext in module.source_files():
		dependency_map[source] = (track_file(module, source, included_dirs, []), ext)
	for dep in module.private_required:
		ok = False
		for d in dep.public_includes:
			if d in included_dirs:
				ok = True
				break
		if not ok:
			utils.warn("Module %s: Useless dependency '%s'" % (module.name, dep.name))
	included_dirs = set()
	for header, ext in module.header_files():
		dependency_map[header] = (track_file(module, header, included_dirs, []), ext)
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
			m_dependency_map[m] = track_module(m) if m.auto_enabled else {} # TODO: ??
		except config.BaseError as e:
			raise config.BaseError("Module %s: %s" % (m.name, str(e)))
	return m_dependency_map
