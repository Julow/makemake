# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_checker.py                                  :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 10:04:05 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/19 16:56:11 by jaguillo         ###   ########.fr        #
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

# Check a module
def _check_module(module, checked_modules):
	if config.MODULE_NAME_REG.match(module.name) == None:
		utils.warn("Module name \"%s\" contains invalid characters" % module.name)
	if not os.path.isdir(module.base_dir):
		raise CheckError("Invalid base dir: %s" % module.base_dir)
	for i in module.public_includes:
		if not os.path.isdir(i):
			raise CheckError("Invalid include: %s" % i)
	for checked in checked_modules:
		if module.base_dir == checked.base_dir:
			raise CheckError("Modules '%s': Have the same base dir: %s" % (
				checked.name, module.base_dir
			))
		for i in module.public_includes:
			if i in checked.public_includes:
				raise CheckError("Modules '%s': Include the same dir (%s)" % (
					checked.name, i
				))
	for inc, _ in module.mk_imports:
		if not os.path.isfile(inc):
			raise CheckError("Imported file '%s' %s" % (
				inc, "is not a valid file" if os.path.exists(inc) else "does not exists"
			))
	if len(module.public_includes) > 1:
		utils.warn("Too many public dirs")

#
# Check for errors
#
# raise a CheckError on error
#
def check(modules):
	checked = []
	module_names = {}
	main_module = None
	for module in modules:
		try:
			if module.name in module_names:
				raise CheckError("redefined")
			module_names[module.name] = module
			_check_module(module, checked)
			checked.append(module)
		except config.BaseError as e:
			raise CheckError("Module %s: %s" % (module.name, str(e)))
		if module.is_main:
			if main_module == None:
				main_module = module
			else:
				raise CheckError("Too many main modules (%s)" % ", ".join([m.name for m in modules if m.is_main]))
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
