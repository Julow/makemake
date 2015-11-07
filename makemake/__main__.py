# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    __main__.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 09:22:52 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/07 00:15:01 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from sys import argv, stdout
import module_searcher
import module_printer
import dependency_finder
import depend_generator
import makefile_generator
import module
import config
import utils
import os

#
# makemake2 [command]
#

#
# TODO: ?path? for full relative path (in module file)
# TODO: public local instruction
# TODO: opti using set and ordered_set
#

def list_command(args):
	modules = module_searcher.parse_all()
	used_map = {}
	used_modules = module_searcher.filter_unused(modules)
	for m in used_modules:
		used_map[m.name] = True
	if len(modules) == 0:
		print "No module found"
	else:
		print "%d \033[90m(+%d unused)\033[0m modules:" % (len(used_modules), len(modules) - len(used_modules))
		max_len = 0
		for m in modules:
			if len(m.name) > max_len:
				max_len = len(m.name)
		for m in sorted(modules, key=lambda m: (m.name in used_map, m.name)):
			f = "%-*s (%s)"
			print ("\t%s" if m.name in used_map else "\t\033[90m%s\033[0m") % f % (
				max_len, m.name, os.path.relpath(m.base_dir)
			)

def check_command(args):
	modules = module_searcher.load()
	dependency_finder.track(modules)
	if len(modules) == 0:
		print "No module found"
	else:
		print "%d modules - OK" % len(modules)

HELP = {
	"list": ("Search and list all modules", """
		Search and list all modules with their base directory
		Take no argument
"""),
	"check": ("Search modules and check for error", """
		Search modules and check for error
		Take no argument
"""),
	"dep": ("Show dependencies for each source of a module", """
		Take module names as argument
"""),
	"info": ("Show info about modules", """
		Take module names as argument
		If called without argument, show info about each modules
"""),
	"put": ("Show variables putted by one or more modules", """
		Take module names as argument
		If called without argument, show var of all modules
"""),
	"gen": ("Generate depend file", """
		Generate a depend file
"""),
	"makefile": ("Create a basic Makefile", """
		Create a basic Makefile
"""),
	"help": ("Show help about a command", """
		Take command names as argument and show their helps
""")
}

def help_command(args):
	if len(args) == 0:
		print "Commands:"
		for cmd in HELP:
			print "\t%-12s %s" % (cmd, HELP[cmd][0])
	else:
		for arg in args:
			if arg in HELP:
				print "\t%-12s %s" % (arg, HELP[arg][0])
				if HELP[arg][1] != None:
					print HELP[arg][1]
			else:
				print "No help for '%s'" % arg

def info_command(args):
	modules = module_searcher.all()
	if len(args) > 0:
		for m_name in args:
			ok = False
			for m in modules:
				if m.name == m_name:
					ok = True
					break
			if not ok:
				raise config.BaseError("Unknow module '%s'" % m_name) # TODO: exception
		arg_modules = []
		for m in modules:
			if m.name in args:
				arg_modules.append(m)
		modules = arg_modules
	for m in modules:
		print "module %s: %s" % (m.name, os.path.relpath(m.base_dir))
		for i in m.public_includes:
			print "\tpublic include %s" % os.path.relpath(i)
		for i in m.private_includes:
			print "\tprivate include %s" % os.path.relpath(i)
		for r in m.public_required:
			print "\tpublic require %s" % r
		for r in m.private_required:
			print "\tprivate require %s" % r
		for p in m.to_put:
			print "\tput %s %s" % (p, " ".join(m.to_put[p]))
		for l in m.locals:
			print "\tlocal %s" % l
		if not m.auto_enabled:
			print "\tdisable auto"
		for (i, c) in m.mk_imports:
			print "\tmakefile %s %s" % ("import" if c else "include", os.path.relpath(i))
		print ""

# dep command
def show_dep(m, sources):
	print "# module %s" % m.name
	for src in sources:
		includes = []
		for i in sources[src][0]:
			includes.append(os.path.relpath(i))
		print "%s: %s" % (os.path.basename(src), " ".join(includes))

def dep_command(args):
	modules = module_searcher.load()
	source_map = dependency_finder.track(modules)
	if len(args) == 0:
		for m in modules:
			show_dep(m, source_map[m])
	else:
		for m_name in args:
			tmp = None
			for m in modules:
				if m.name == m_name:
					tmp = m
					break
			if tmp == None:
				raise config.BaseError("Unknow module '%s'" % m_name) # TODO: exception
			if tmp in source_map:
				show_dep(tmp, source_map[tmp])
			else:
				raise config.BaseError("WTF happen with module '%s'" % m_name)

def put_command(args):
	put = {}
	for m in module_searcher.load():
		if len(args) > 0 and not m.name in args:
			continue
		for var in m.to_put:
			if not var in put:
				put[var] = []
			for word in m.to_put[var]:
				if not word in put[var]:
					put[var].append(word)
	for var in put.keys():
		print "%s = %s" % (var, " ".join(put[var]))

def debug_command(args):
	print ""

def gen_command(args):
	modules = module_searcher.load()
	source_map = dependency_finder.track(modules)
	depend_generator.gen(config.DEPEND_FILE_NAME, modules, source_map)

def makefile_command(args):
	if os.path.exists(config.MAKEFILE_NAME):
		print "Makefile already exists"
	else:
		makefile_generator.gen(config.MAKEFILE_NAME)

def print_command(args):
	file_name = module_printer.gen(module_searcher.load())
	print "Module tree generated to %s" % file_name
	utils.open_browser(file_name)

COMMANDS = {
	"list": list_command,
	"check": check_command,
	"help": help_command,
	"dep": dep_command,
	"info": info_command,
	"put": put_command,
	"gen": gen_command,
	"makefile": makefile_command,
	"print": print_command,
	"debug": debug_command,
}

def main():
	try:
		argv[0] = "makemake" # because fuck
		if len(argv) > 1:
			if argv[1] in COMMANDS:
				COMMANDS[argv[1]](argv[2:])
			else:
				raise config.BaseError("Unknow command '%s'" % argv[1]) # TODO: exception
		else:
			print "%s: Available commands: %s" % (argv[0], ", ".join(sorted(COMMANDS.keys())))
			print "Type '%s help' for help" % argv[0]
			return 2
	except config.BaseError as e:
		print "\033[31mError:\033[0m %s" % str(e)
		return 1
	except Exception as e:
		raise
	return 0

if __name__ == '__main__':
	exit(main())
