# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/14 22:44:53 by juloo             #+#    #+#              #
#    Updated: 2015/11/05 00:20:00 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import config

#
# Represent a module
#
class Module():

	def __init__(self, module_name, base_dir):

		self.name = module_name
		self.base_dir = base_dir
		self.public_includes = []
		self.private_includes = []
		self.public_required = []
		self.private_required = []
		self.to_put = {}
		self.locals = []
		self.auto_enabled = True
		self.mk_imports = []

	def include(self, dirs, public):
		for d in dirs:
			d = os.path.join(self.base_dir, d)
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
