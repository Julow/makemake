# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/14 22:44:53 by juloo             #+#    #+#              #
#    Updated: 2015/11/17 01:13:54 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import re
import config

INCLUDE_REG = re.compile(config.INCLUDE_REG)

#
# Represent a module
#
class Module():

	def __init__(self, module_name, base_dir):

		# Module definitions
		self.name = module_name
		self.base_dir = os.path.abspath(base_dir)
		self.public_includes = []
		self.private_includes = []
		self.public_required = []
		self.private_required = []
		self.to_put = {}
		self.locals = []
		self.auto_enabled = True
		self.mk_imports = []

		self.is_main = False

		self._source_dirs = []

		# -
		self._source_files = None
		self._header_files = None

		self._include_map = None

		self._private_dirs = None

	# Return list of source directories
	def source_dirs(self):
		if len(self._source_dirs) == 0:
			return [self.base_dir]
		return self._source_dirs

	# Return a list of source file
	def source_files(self):
		if self._source_files == None:
			self._find_file()
		return self._source_files

	# Return a list of header file
	def header_files(self):
		if self._header_files == None:
			self._find_file()
		return self._header_files

	# Return a list of directly included files {file_name: [includes]}
	def include_map(self):
		if self._include_map == None:
			self._include_map = {}
			for file_name, _ in self.source_files() + self.header_files():
				included = []
				with open(file_name, "r") as f:
					for line in f:
						m = INCLUDE_REG.match(line)
						if m != None and m.group(1) != None:
							included.append(m.group(1))
				self._include_map[file_name] = included
		return self._include_map

	# Return a list of direct included dirs [(module, dir)]
	def private_dirs(self):
		if self._private_dirs == None:
			self._private_dirs = []
			self._private_dirs += [(self, i) for i in self.public_includes]
			self._private_dirs += [(self, i) for i in self.private_includes]
			for m in self.public_required + self.private_required:
				self._private_dirs += [(m, i) for i in m.public_includes]
		return self._private_dirs

	# Return a list of recursively included dirs [(module, dir)]
	def included_dirs(self, private = True):
		def helper(required, includes):
			dirs = [(self, i) for i in includes]
			for r in required:
				for d in r.included_dirs(False):
					if not d in dirs:
						dirs.append(d)
			return dirs
		dirs = helper(self.public_required, self.public_includes)
		if private:
			dirs += helper(self.private_required, self.private_includes)
		return dirs

	# Return a list of recursively required modules
	def required_modules(self, private = True):
		def helper(required):
			modules = required
			for r in required:
				for d in r.required_modules(False):
					if not d in modules:
						modules.append(d)
			return modules
		modules = helper(self.public_required)
		if private:
			modules += helper(self.private_required)
		return modules

	# load source_files and header_files
	def _find_file(self):
		self._source_files = []
		self._header_files = []
		if self.auto_enabled:
			for source_dir in self.source_dirs():
				for curr_dir, dirs, ls in os.walk(source_dir):
					if os.path.basename(curr_dir) in config.EXCLUDE_DIRS or curr_dir in self.public_includes:
						del dirs[:]
					else:
						for file_name in ls:
							for ext in config.EXTENSIONS:
								if file_name.endswith(ext["ext"]):
									self._source_files.append((os.path.join(curr_dir, file_name), ext))
		for inc_dir in self.public_includes:
			for curr_dir, dirs, ls, in os.walk(inc_dir):
				if os.path.basename(curr_dir) in config.EXCLUDE_DIRS:
					del dirs[:]
				else:
					for file_name in ls:
						for ext in config.EXTENSIONS:
							if file_name.endswith(ext["ext"]):
								self._header_files.append((os.path.join(curr_dir, file_name), ext))

	#
	# instructions
	#
	def include(self, dirs, public):
		for d in dirs:
			d = os.path.abspath(os.path.join(self.base_dir, d))
			if public:
				if not d in self.public_includes:
					self.public_includes.append(d)
			else:
				if not d in self.private_includes:
					self.private_includes.append(d)

	def require(self, module, public):
		if public:
			if not module in self.public_required:
				self.public_required.append(module)
		else:
			if not module in self.private_required:
				self.private_required.append(module)

	def source(self, words):
		for w in words:
			if not w in self._source_dirs:
				self._source_dirs.append(w)

	def put(self, var, words):
		if not var in self.to_put:
			self.to_put[var] = []
		for w in words:
			if not w in self.to_put[var]:
				self.to_put[var].append(w)

	def local(self, code):
		self.locals.append(code)

	def disable(self, key):
		if key == "auto":
			self.auto_enabled = False
		else:
			raise "Cannot disable %s" % key

	def mk_import(self, file_name, copy):
		self.mk_imports.append((os.path.join(self.base_dir, file_name), copy))

#
# Check if 'file_name' exists in a dir of 'dir_list'
# 'dir_list' is a list of tuple (dir_name, data)
# Return a full path and the corresponding data or None if not found
#

def _source_in_dirs(file_name, dir_list):
	for dir_name, data in dir_list:
		tmp = os.path.join(dir_name, file_name)
		if os.path.isfile(tmp):
			return (tmp, data)
	return None

#
# Concat all 'put' values
# Return a map {var_name: [words]}
#

def get_puts(module_list):
	put = {}
	for m in module_list:
		for var in m.to_put:
			if not var in put:
				put[var] = []
			for word in m.to_put[var]:
				if not word in put[var]:
					put[var].append(word)
	return put

#
# Return default ?variables? for a module
#

def get_variables(module):
	return {
		"path": os.path.relpath(module.base_dir),
		"name": module.name
	}
