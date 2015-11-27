# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    depend_generator.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/31 16:18:31 by juloo             #+#    #+#              #
#    Updated: 2015/11/27 15:38:21 by juloo            ###   ########.fr        #
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
	# Out vars
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
	links = out_link_vars(out, modules)
	for m in modules:
		out_module(out, m, obj_files[m])
	out_obj_dirs(out, obj_files)
	out_link_rules(out, links)
	out_dependencies(out, modules, source_map, obj_files)

#

def out_link_vars(out, modules):
	base_link_dir = os.path.join(config.OBJ_DIR, config.PUBLIC_LINK_DIR)
	link_dirs = set()
	links = []
	for m in modules:
		base_dir = os.path.join(base_link_dir, "/".join(m.name.split(config.NAMESPACES_SEPARATOR)[0:-1]))
		for header, _, inc_dir in m.header_files():
			h_link = os.path.join(base_dir, os.path.relpath(header, inc_dir))
			tmp = h_link
			while len(tmp) > len(base_link_dir):
				tmp = os.path.dirname(tmp)
				link_dirs.add(tmp)
			links.append((h_link, header))
	# INCLUDE_FLAGS var
	prefix = "%s +=" % config.INCLUDE_FLAGS_VAR
	out.write(prefix)
	print_file_list(out, ["-I%s" % base_link_dir], len(prefix))
	out.write("\n")
	# PUBLIC_LINKS var
	prefix = "%s +=" % config.PUBLIC_LINKS_VAR
	out.write(prefix)
	print_file_list(out, [l for l, _ in links], len(prefix))
	out.write("\n")
	# PUBLIC_LINK_DIRS var
	prefix = "%s +=" % config.PUBLIC_LINK_DIRS
	out.write(prefix)
	print_file_list(out, ["%s/" % d for d in sorted(link_dirs)], len(prefix))
	out.write("\n")
	out.write("\n")
	out.write("$(%s): | $(%s)\n" % (config.PUBLIC_LINKS_VAR, config.PUBLIC_LINK_DIRS))
	out.write("\n")
	return links

#

def out_link_rules(out, links):
	out.write("# public links\n")
	for link, dst in links:
		print_file_list(out, ["%s:" % link, os.path.relpath(dst)], 0, "")
		out.write("\n")
	out.write("\n")

#

def out_module(out, mod, obj_files):
	out.write("# module %s\n" % mod.name)
	obj_names = sorted(obj_files.keys())
	# mk imports
	for file_name, copy in mod.mk_imports:
		if copy:
			with open(file_name) as f:
				out.write(utils.substitute_vars(f.read(), module.get_variables(mod)))
		else:
			out.write("include %s" % os.path.relpath(file_name))
	# rules
	for o_file in obj_names:
		prefix = "%s:" % o_file
		out.write(prefix)
		print_file_list(out, [os.path.relpath(obj_files[o_file])], len(prefix))
		out.write("\n")
	# locals
	if len(obj_names) > 0 and len(mod.locals) > 0:
		out.write("\n")
		for l in mod.locals:
			sep = ":"
			offset = print_file_list(out, obj_names, 0, "") + len(sep)
			out.write(sep)
			print_file_list(out, [l], offset)
			out.write("\n")
	out.write("\n")

#

def out_obj_dirs(out, obj_files):
	out.write("# obj dirs\n")
	for m in obj_files:
		obj_dirs = set()
		for obj in obj_files[m]:
			obj_dirs.add(os.path.dirname(obj))
		if len(obj_dirs) > 0:
			sep = ":"
			offset = print_file_list(out, obj_files[m].keys(), 0, "") + len(sep)
			out.write(sep)
			print_file_list(out, ["|"] + ["%s/" % d for d in sorted(obj_dirs)], offset)
			out.write("\n")
	out.write("\n")

#

def out_dependencies(out, modules, src_files, obj_files):
	out.write("# dependencies\n")
	for m in obj_files:
		for o_file in obj_files[m]:
			dependencies = [os.path.relpath(f) for f in sorted(src_files[m][obj_files[m][o_file]][0])]
			prefix = "%s:" % o_file
			out.write(prefix)
			print_file_list(out, dependencies, len(prefix))
			out.write("\n")

#
#
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
		print_file_list(out, p, len(prefix))
		out.write("\n")

#

def print_file_list(out, files, offset, indent = "\t", sep = " ", endl = " \\"):
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
