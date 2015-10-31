# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    depend_generator.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/31 16:18:31 by juloo             #+#    #+#              #
#    Updated: 2015/10/31 17:33:18 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import module_def
import config

#
# Output a depend.mk to 'out'
#

def out(out, modules, source_map):
	obj_files = {}
	obj_file_list = []
	for m in modules:
		o = get_obj_files(source_map[m])
		obj_file_list += o
		obj_files[m] = o
	out_puts(modules, {"O_FILES": obj_file_list})
	for m in modules:
		print ""
		print "# module %s" % m.module_name
		out_targets(m)
		out_autos(m, source_map[m], obj_files[m])

#

def get_obj_files(sources):
	obj_files = {}
	for s in sources:
		o = s[:-len(sources[s][1]["ext"])] + sources[s][1]["obj_ext"]
		o = os.path.join(config.OBJ_DIR, os.path.relpath(o))
		obj_files[o] = s
	return obj_files

#

def out_puts(modules, extra):
	puts = module_def.get_puts(modules)
	for var in puts.keys() + extra.keys():
		p = puts[var] if var in puts else []
		if var in extra:
			p += extra[var]
		print "%s += %s" % (var, " ".join(p))

def out_targets(module):
	for target in module.targets:
		print target[0]
		for r in target[1]:
			print "\t%s" % r

def out_autos(module, sources, obj_files):
	for o_file in obj_files:
		s_file = obj_files[o_file]
		dependencies = [os.path.relpath(f) for f in sources[s_file][0] + [s_file]]
		for l in module.locals:
			print "%s: %s" % (o_file, l)
		print "%s: %s | %s" % (o_file, " ".join(dependencies), os.path.dirname(o_file))
