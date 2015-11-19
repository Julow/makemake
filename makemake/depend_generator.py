# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    depend_generator.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/31 16:18:31 by juloo             #+#    #+#              #
#    Updated: 2015/11/19 16:18:18 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import module
import config
import utils

#
# Overwrite file_name
#
def gen(file_name, modules, source_map):
	with open(file_name, "w") as f:
		out(f, modules, source_map)

#
# Output a depend file to 'out'
#

def out(out, modules, source_map):
	obj_files = {}
	sorted_modules = sorted(modules, key=lambda m: m.name)
	obj_file_list = []
	for m in sorted_modules:
		o = get_obj_files(source_map[m])
		obj_file_list += sorted(o.keys())
		obj_files[m] = o
	public_dirs = []
	for m in sorted_modules:
		if len(m.public_includes) > 0:
			public_dirs += sorted([os.path.relpath(p) for p in m.public_includes])
	out_puts(out, modules, {
		"O_FILES": obj_file_list
		# "PUBLIC_DIRS": public_dirs
	})
	for m in modules:
		out.write("\n# module %s\n" % m.name)
		out_mk_imports(out, m)
		out_inc_links(out, m, obj_files[m])
		out_locals(out, m, obj_files[m])
		out_autos(out, modules, m, source_map[m], obj_files[m])

#

def get_obj_files(sources):
	obj_files = {}
	for s in sources:
		if not sources[s][1]["is_source"]:
			continue
		o = s[:-len(sources[s][1]["ext"])] + sources[s][1]["obj_ext"]
		o = os.path.join(config.OBJ_DIR, os.path.relpath(o))
		obj_files[o] = s
	return obj_files

#

def out_puts(out, modules, extra):
	puts = module.get_puts(modules)
	for var in sorted(puts.keys() + extra.keys()):
		p = puts[var] if var in puts else []
		if var in extra:
			p = p + extra[var]
		prefix = "%s +=" % var
		out.write(prefix)
		print_file_list(out, p, len(prefix), "\t", " ", " \\")
		out.write("\n")

def out_mk_imports(out, mod):
	for file_name, copy in mod.mk_imports:
		if copy:
			with open(file_name) as f:
				out.write(utils.substitute_vars(f.read(), module.get_variables(mod)))
		else:
			out.write("include %s" % os.path.relpath(file_name))

def out_inc_links(out, module, obj_files):
	link_dir = os.path.join(config.OBJ_DIR, os.path.relpath(module.base_dir), config.PUBLIC_LINK_DIR)
	links = []
	for dep in module.required_modules() + [module]:
		if len(dep.public_includes) == 0:
			continue
		link = os.path.join(link_dir, dep.name)
		dep_dir = os.path.relpath(dep.public_includes[0])
		links.append((link, dep_dir))
	if len(links) == 0:
		return
	prefix = ":"
	offset = print_file_list(out, [l for l, _ in links], 0, "", " ", " \\") + len(prefix)
	out.write(prefix)
	print_file_list(out, ["| %s/" % link_dir], offset, "\t", " ", " \\")
	out.write("\n")
	for link, dep_dir in links:
		prefix = "%s:" % link
		out.write(prefix)
		print_file_list(out, [dep_dir], len(prefix), "\t", " ", " \\")
		out.write("\n")
	out.write("\n")
	prefix = "PUBLIC_LINKS +="
	out.write(prefix)
	print_file_list(out, [l for l, _ in links], len(prefix), "\t", " ", " \\")
	out.write("\n")
	out.write("\n")
	obj_names = sorted(obj_files.keys())
	prefix = ":"
	offset = print_file_list(out, obj_names, 0, "", " ", " \\") + len(prefix)
	out.write(prefix)
	print_file_list(out, [config.INCLUDE_FLAGS_VAR, "+=", "-I%s" % link_dir] + ["-I%s" % os.path.relpath(d) for d in module.private_includes], offset, "\t", " ", " \\")
	out.write("\n")
	prefix = ":"
	offset = print_file_list(out, obj_names, 0, "", " ", " \\") + len(prefix)
	out.write(prefix)
	print_file_list(out, ["|"] + [l for l, _ in links], offset, "\t", " ", " \\")
	out.write("\n")
	out.write("\n")

def out_locals(out, module, obj_files):
	obj_names = sorted(obj_files.keys())
	if len(obj_names) == 0:
		return
	for l in module.locals:
		print_file_list(out, obj_names, 0, "", " ", " \\")
		out.write(": %s\n" % l)
	# prefix = ": %s +=" % config.INCLUDE_FLAGS_VAR
	# offset = len(prefix) + print_file_list(out, obj_names, 0, "", " ", " \\")
	# out.write(prefix)
	# print_file_list(out, ["-I" + os.path.relpath(i) for _, i in sorted(module.included_dirs())], offset, "\t", " ", " \\")
	# out.write("\n")

def out_autos(out, module_list, module, sources, obj_files):
	obj_keys = sorted(obj_files.keys())
	# # do for o_dir and public_links dependencies
	# dep_map = {} # map<list<.o>, list<(.h, bool)>>
	# for o_file in obj_keys:
	# 	s_file = obj_files[o_file]
	# 	headers = sources[s_file][0]
	# 	for h_file in headers: # TODO cat all headers in a set
	# 		dep_by = set()
	# 		for o in obj_keys:
	# 			if h_file in sources[obj_files[o]][0]:
	# 				dep_by.add(o)
	# 		dep_by = tuple(dep_by)
	# 		if dep_by in dep_map:
	# 			dep_map[dep_by].add((h_file, True))
	# 		else:
	# 			dep_map[dep_by] = set([(h_file, True)])
	# # for o_file in obj_keys:
	# 	# do "| dir" rules
	# for dep_by in dep_map:
	# 	sep = ":"
	# 	offset = print_file_list(out, dep_by, 0, "", " ", " \\") + len(sep)
	# 	out.write(sep)
	# 	print_file_list(out, sorted([os.path.relpath(h) for h in dep_map[dep_by]]), offset, "\t", " ", " \\")
	# 	out.write("\n")
	# for o_file in obj_keys:
	# 	s_file = obj_files[o_file]
	# 	print_file_list(out, ["%s:" % o_file, os.path.relpath(s_file)], 0, "\t", " ", " \\")
	# 	out.write("\n")
	# # lol
	for o_file in obj_keys:
		s_file = obj_files[o_file]
		dependencies = [os.path.relpath(f) for f in [s_file] + sorted(sources[s_file][0])]
		prefix = "%s:" % o_file
		dep_list = dependencies + ["| %s/" % os.path.dirname(o_file)]
		out.write(prefix)
		print_file_list(out, dep_list, len(prefix), "\t", " ", " \\")
		out.write("\n")

#

def print_file_list(out, files, offset, indent, sep, endl):
	indent_len = len(indent.expandtabs(4))
	sep_len = len(sep)
	endl_len = len(endl)
	for f in files:
		if (len(f) + offset + sep_len + endl_len) > config.MAX_LINE_LENGTH and offset != indent_len:
			offset = indent_len
			out.write(endl)
			out.write("\n")
			out.write(indent)
		if offset > indent_len:
			out.write(sep)
			offset += sep_len
		out.write(f)
		offset += len(f)
	return offset
