# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    namespaces.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/21 13:48:40 by juloo             #+#    #+#              #
#    Updated: 2015/11/21 17:15:31 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config

class ModuleNamespace():

	def __init__(self, name):

		self.name = name
		self.subs = {}
		self.modules = []

#
# Build a namespace tree and do some check
#
def tree(module_list):
	root = ModuleNamespace(None)
	for m in module_list:
		curr_ns = root
		for ns in m.name.split(config.NAMESPACES_SEPARATOR)[:-1]:
			if not ns in curr_ns.subs:
				curr_ns.subs[ns] = ModuleNamespace(ns)
			curr_ns = curr_ns.subs[ns]
		curr_ns.modules.append(m)
	return root
