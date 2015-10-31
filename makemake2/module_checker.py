# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_checker.py                                  :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 10:04:05 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/31 18:34:13 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import config

class CheckError(config.BaseError):

	def __init__(self, err):
		super(CheckError, self).__init__(err)

#
# Check for errors
#
# raise a CheckError on error
#
def check(modules):
	checked = []
	module_names = {}
	for m in modules:
		if m.module_name in module_names:
			raise CheckError("Module '%s' redefined" % m.module_name)
		module_names[m.module_name] = True
		if not os.path.isdir(m.base_dir):
			raise CheckError("Invalid base dir for module '%s' (%s)" % (m.module_name, m.base_dir))
		for i in m.public_includes:
			if not os.path.isdir(i):
				raise CheckError("Invalid include for module '%s' (%s)" % (m.module_name, i))
		for checked_module in checked:
			if m.base_dir == checked_module.base_dir:
				raise CheckError("Modules '%s' and '%s' have the same dir (%s)" % (
					m.module_name, checked_module.module_name, m.base_dir
				))
			for i in m.public_includes:
				if i in checked_module.public_includes:
					raise CheckError("Modules '%s' and '%s' include the same dir (%s)" % (
						m.module_name, checked_module.module_name, i
					))
		checked.append(m)
	for m in modules:
		for r in m.public_required:
			if not r in module_names:
				raise CheckError("Unknow module '%s' (publicly required by '%s')" % (r, m.module_name))
		for r in m.private_required:
			if not r in module_names:
				raise CheckError("Unknow module '%s' (privately required by '%s')" % (r, m.module_name))
	return True
