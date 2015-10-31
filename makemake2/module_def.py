# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_def.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/14 22:44:53 by juloo             #+#    #+#              #
#    Updated: 2015/10/31 18:11:35 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os

#
# Represent a module declaration
#
class ModuleDef():

	def __init__(self, module_name, base_dir):

		self.module_name = module_name
		self.base_dir = base_dir
		self.include_dirs = []
		self.public_required = []
		self.private_required = []
		self.to_put = {}
		self.locals = []
		self.auto_enabled = True
		self.defaultRecipes = []
		self.targets = []

	def include(self, dirs):
		for d in dirs:
			if not d.startswith("/"):
				d = os.path.join(self.base_dir, d)
			if not d in self.include_dirs:
				self.include_dirs.append(d)

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

	def recipe(self, code):
		if len(self.targets) == 0:
			self.defaultRecipes.append(code)
		else:
			self.targets[-1][1].append(code)

	def target(self, code):
		self.targets.append((code, []))

	# debug
	def __str__(self):
		s = "Module %s\n" % self.module_name
		s += "%24s: %s\n" % ("base dir", self.base_dir)
		s += "%24s: %s\n" % ("public dirs", ", ".join(self.include_dirs))
		s += "%24s: %s\n" % ("public require", ", ".join(self.public_required))
		s += "%24s: %s\n" % ("private require", ", ".join(self.private_required))
		for v in self.to_put:
			s += "%24s: %s\n" % ("put to %s" % v, ", ".join(self.to_put[v]))
		for l in self.locals:
			s += "%24s: %s\n" % ("local", l)
		if not self.auto_enabled:
			s += "%24s: auto\n" % "disable"
		if len(self.defaultRecipes) > 0:
			s += "%24s:\n" % "default recipes"
			for r in self.defaultRecipes:
				s += "%28s%s\n" % (' ', r)
		for t, recipes in self.targets:
			s += "%24s: %s\n" % ("target", t)
			for r in recipes:
				s += "%28s%s\n" % (' ', r)
		return s

#
# Search a module by name in a module list
#

def get_module(module_list, name):
	for m in module_list:
		if m.module_name == name:
			return m
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
