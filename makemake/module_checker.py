# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_checker.py                                  :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 10:04:05 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/08 20:09:12 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import config
import utils

class CheckError(config.BaseError):

	def __init__(self, err):
		super(CheckError, self).__init__(err)

# TODO: ordered_set
def check_include_loop(module, include_stack):
	include_stack.append(module.name)
	def loop(l):
		for m in l:
			if m.name in include_stack:
				raise CheckError("Include loop: %s --> %s" % (
					" --> ".join(include_stack), m.name
				))
			check_include_loop(m, include_stack)
	loop(module.public_required)
	loop(module.private_required)
	include_stack.pop()

#
# Check for errors
#
# raise a CheckError on error
#
def check(modules):
	checked = []
	module_names = {}
	module_map = {}
	main_module = None
	for module in modules:
		if module.name in module_names:
			raise CheckError("Module '%s' redefined" % module.name)
		module_names[module.name] = module
		module_map[module] = True
		if not os.path.isdir(module.base_dir):
			raise CheckError("Invalid base dir for module '%s' (%s)" % (module.name, module.base_dir))
		for i in module.public_includes:
			if not os.path.isdir(i):
				raise CheckError("Invalid include for module '%s' (%s)" % (module.name, i))
		for checked_module in checked:
			if module.base_dir == checked_module.base_dir:
				raise CheckError("Modules '%s' and '%s' have the same dir (%s)" % (
					module.name, checked_module.name, module.base_dir
				))
			for i in module.public_includes:
				if i in checked_module.public_includes:
					raise CheckError("Modules '%s' and '%s' include the same dir (%s)" % (
						module.name, checked_module.name, i
					))
		for inc, _ in module.mk_imports:
			if not os.path.isfile(inc):
				raise CheckError("File '%s' %s (included from module %s)" % (
					inc, "is not a valid file" if os.path.exists(inc) else "does not exists", module.name
				))
		if module.is_main:
			if main_module == None:
				main_module = module
			else:
				raise CheckError("Too many main modules (%s)" % ", ".join([m.name for m in modules if m.is_main]))
		checked.append(module)
	if main_module == None:
		utils.warn("Main module missing")
	for module in modules:
		def check_dep(lst):
			for r in lst:
				if r.is_main:
					utils.warn("Main module %s: Should be the root module (required by %s) (it'll cause an include loop)" % (r.name, module.name))
		check_dep(module.public_required)
		check_dep(module.private_required)
	for module in modules:
		check_include_loop(module, [])
	return True
