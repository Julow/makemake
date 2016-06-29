# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    depend_generator.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/31 16:18:31 by juloo             #+#    #+#              #
#    Updated: 2016/06/29 22:56:12 by juloo            ###   ########.fr        #
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
	modules = sorted(modules, key=lambda m: m.name)
	obj_files, links, mains, extra_vars = get_vars(modules, source_map)
	out_puts(out, modules, extra_vars)
	out_mains(out, mains)
	for m in modules:
		out_module(out, m, source_map[m], obj_files[m])
	out_link_rules(out, links)

#

def get_vars(modules, source_map):
	# Links
	base_link_dir = os.path.join(config.OBJ_DIR, config.PUBLIC_LINK_DIR)
	link_dirs = []
	links = []
	for m in modules:
		base_dir = os.path.join(base_link_dir, "/".join(m.name.split(config.NAMESPACES_SEPARATOR)[0:-1]))
		for header, _, inc_dir in m.header_files():
			h_link = os.path.join(base_dir, os.path.relpath(header, inc_dir))
			link_dirs.append(h_link)
			links.append((h_link, header))
	# Obj files
	obj_files = {}
	obj_file_list = []
	for m in modules:
		o = get_obj_files(source_map[m])
		obj_file_list += sorted(o.keys())
		obj_files[m] = o
	# Obj dirs
	obj_dirs = set()
	for d in [os.path.dirname(d) for d in obj_file_list + link_dirs]:
		tmp = d
		while len(tmp) >= len(config.OBJ_DIR):
			obj_dirs.add(tmp)
			tmp = os.path.dirname(tmp)
	# Main modules
	mains = [m for m in modules if m.is_main]
	# Puts
	puts = {
		config.INCLUDE_FLAGS_VAR: ["-I%s" % base_link_dir],
		config.PUBLIC_LINKS_VAR: sorted([l for l, _ in links]),
		config.OBJ_FILES_VAR: obj_file_list,
		config.OBJ_DIR_TREE_VAR: ["%s/" % d for d in sorted(obj_dirs, reverse=True)],
		config.MAINS_VAR: [m.name for m in mains],
	}
	# -
	return (obj_files, sorted(links), mains, puts)

#

def out_mains(out, mains):
	if len(mains) == 1:
		out.write("%s: $(%s)\n\n" % (mains[0].name, config.OBJ_FILES_VAR))
		return
	def track_sources(m, sources):
		for f in m.source_files():
			sources[f[0]] = f
		for m in m.required_modules():
			track_sources(m, sources)
	for t in mains:
		srcs = {}
		track_sources(t, srcs)
		prefix = "%s:" % t.name
		out.write(prefix)
		print_file_list(out, map(os.path.relpath, get_obj_files(srcs).keys()), len(prefix))
		out.write("\n\n")

#

def out_link_rules(out, links):
	out.write("# public links\n")
	for link, dst in links:
		print_file_list(out, ["%s:" % link, os.path.relpath(dst)], 0, "")
		out.write("\n")

#

def out_module(out, mod, src_files, obj_files):
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
		dependencies = [os.path.relpath(f) for f in [obj_files[o_file]] + sorted(src_files[obj_files[o_file]][0])]
		prefix = "%s:" % o_file
		out.write(prefix)
		print_file_list(out, dependencies, len(prefix))
		out.write("\n")
	# locals
	lvars = mod.locals
	if len(mod.private_includes) > 0:
		lvars += ["INCLUDE_FLAGS += %s" % " ".join(["-I%s" % os.path.relpath(d) for d in mod.private_includes])]
	if len(obj_names) > 0 and len(lvars) > 0:
		out.write("\n")
		for l in lvars:
			sep = ":"
			offset = print_file_list(out, obj_names, 0, "") + len(sep)
			out.write(sep)
			print_file_list(out, l.split(), offset)
			out.write("\n")
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
