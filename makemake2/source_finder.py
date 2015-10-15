# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    source_finder.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 12:58:39 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/15 16:39:59 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import config
import re

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
# Search source files in a dir
#  return a list of absolute path to the sources
#

def find(start_dir):
	sources = []
	for curr_dir, dirs, ls in os.walk(start_dir):
		if os.path.basename(curr_dir) in config.EXCLUDE_DIRS:
			del dirs[:]
		else:
			for file_name in ls:
				for ext in config.SOURCE_EXT:
					if file_name.endswith(ext):
						sources.append(os.path.join(curr_dir, file_name))
						break
	return sources
#
# Search source files
#  return a map {source_name: dependencies}
#

def track(search_dir, include_dirs):
	dep = DependencyMap(include_dirs)
	for f in find(search_dir):
		dep.track(os.path.abspath(f))
	return dep.map

#
#
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
				))
		self.map[file_name] = includes
		return includes
