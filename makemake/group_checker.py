# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    group_checker.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/19 17:02:48 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/19 17:40:58 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

class ModuleGroup():

	def __init__(self, group_name):

		self.name = group_name
		self.sub_groups = {}
		self.modules = []

#
# Build a group tree and do some check
# The root group name is None
#
def tree(module_list):
	root = ModuleGroup(None)
	for m in module_list:
		curr_group = root
		for g in m.groups:
			if not g in curr_group.sub_groups:
				curr_group.sub_groups[g] = ModuleGroup(g)
			curr_group = curr_group.sub_groups[g]
		curr_group.modules.append(m)
	return root
