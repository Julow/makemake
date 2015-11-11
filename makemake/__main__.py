# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    __main__.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 09:22:52 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/11 02:01:02 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from sys import argv, stdout
import module_searcher
import module_printer
import module_checker
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

# list command

def list_command(args):
	modules = module_searcher.parse_all()
	used_map = {}
	used_modules = module_searcher.filter_unused(modules)
	for m in used_modules:
		used_map[m.name] = True
	if len(modules) == 0:
		print "No module found"
	else:
		unused_count = len(modules) - len(used_modules)
		extra = "" if unused_count == 0 else "\033[90m(+%d unused)\033[0m " % unused_count
		print "%d %smodule%s:" % (len(modules), extra, "s" if len(modules) > 1 else "")
		max_len = 0
		for m in modules:
			if len(m.name) > max_len:
				max_len = len(m.name)
		for m in sorted(modules, key=lambda m: (m.name in used_map, m.name)):
			f = "%-*s (%s)"
			print ("\t%s" if m.name in used_map else "\t\033[90m%s\033[0m") % f % (
				max_len, m.name, os.path.relpath(m.base_dir)
			)

# check command

def check_command(args):
	modules = module_searcher.parse_all()
	module_checker.check(modules)
	dependency_finder.track(modules)
	if len(modules) == 0:
		print "No module found"
	else:
		print "%d modules - OK" % len(modules)

# help command

HELP = {
	"list": ("Search and list all modules", """
		Search and list all modules with their base directory
		Take no argument
"""),
	"check": ("Search modules and check for error", """
		Search modules and check for error
		Take no argument
"""),
	"info": ("Show info about modules, puts, ...", """
		Commands available:
			info modules	Show module declarations
			info put		Show put'd variables (put instruction)
			info dep		Show dependencies

		Take module names as argument
		If called without argument, show info of all modules
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
		for cmd in sorted(HELP.keys()):
			print "\t%-12s %s" % (cmd, HELP[cmd][0])
	else:
		for arg in args:
			if arg in HELP:
				print "\t%-12s %s" % (arg, HELP[arg][0])
				if HELP[arg][1] != None:
					print HELP[arg][1]
			else:
				print "No help for '%s'" % arg

# info command

def _info_modules(args):
	modules = module_searcher.load()
	if len(args) == 0:
		return modules
	arg_modules = []
	for m_name in args:
		ok = False
		for m in modules:
			if m.name == m_name:
				arg_modules.append(m)
				ok = True
				break
		if not ok:
			raise config.BaseError("Unknown module '%s'" % m_name) # TODO: exception
	return arg_modules

def info_modules_command(args):
	for m in _info_modules(args):
		print "module %s: %s/" % (m.name, os.path.relpath(m.base_dir))
		for i in m.public_includes:
			print "\tpublic include %s/" % os.path.relpath(i, m.base_dir)
		for i in m.private_includes:
			print "\tprivate include %s/" % os.path.relpath(i, m.base_dir)
		for r in m.public_required:
			print "\tpublic require %s" % r.name
		for r in m.private_required:
			print "\tprivate require %s" % r.name
		for p in m.to_put:
			print "\tput %s %s" % (p, " ".join(m.to_put[p]))
		for l in m.locals:
			print "\tlocal %s" % l
		if not m.auto_enabled:
			print "\tdisable auto"
		for (i, c) in m.mk_imports:
			print "\tmakefile %s %s" % ("import" if c else "include", os.path.relpath(i, m.base_dir))
		print ""

def info_puts_command(args):
	puts = {}
	for m in _info_modules(args):
		for var in m.to_put:
			if not var in puts:
				puts[var] = []
			for word in m.to_put[var]:
				if not word in puts[var]:
					puts[var].append(word)
	for var in puts:
		print "%s = %s" % (var, " ".join(puts[var]))

def info_dep_command(args):
	modules = _info_modules(args)
	source_map = dependency_finder.track(modules)
	for m in modules:
		print "# module %s" % m.name
		for src in source_map[m]:
			includes = []
			for i in source_map[m][src][0]:
				includes.append(os.path.relpath(i))
			print "%s: %s" % (os.path.basename(src), " ".join(includes))

INFO_COMMANDS = {
	"modules": info_modules_command,
	"put": info_puts_command,
	"dep": info_dep_command
};

def info_command(args):
	if len(args) > 0:
		if args[0] in INFO_COMMANDS:
			INFO_COMMANDS[args[0]](args[1:])
			return
		utils.error("Unknown info command %s" % args[0])
	print "Info commands: %s" % " ".join(sorted(INFO_COMMANDS.keys()))

# gen command

def gen_command(args):
	modules = module_searcher.load()
	source_map = dependency_finder.track(modules)
	depend_generator.gen(config.DEPEND_FILE_NAME, modules, source_map)

# makefile command

def makefile_command(args):
	if os.path.exists(config.MAKEFILE_NAME):
		print "Makefile already exists"
	else:
		makefile_generator.gen(config.MAKEFILE_NAME)

# print command

def print_command(args):
	file_name = module_printer.gen(module_searcher.load())
	print "Module tree generated to %s" % file_name
	utils.open_browser(file_name)

COMMANDS = {
	"list": list_command,
	"check": check_command,
	"help": help_command,
	"info": info_command,
	"gen": gen_command,
	"makefile": makefile_command,
	"print": print_command,
}

def main():
	try:
		argv[0] = "makemake" # because fuck
		if len(argv) > 1:
			if argv[1] in COMMANDS:
				COMMANDS[argv[1]](argv[2:])
			else:
				raise config.BaseError("Unknown command '%s'" % argv[1]) # TODO: exception
		else:
			print "%s: Available commands: %s" % (argv[0], ", ".join(sorted(COMMANDS.keys())))
			print "Type '%s help' for help" % argv[0]
			return 2
	except config.BaseError as e:
		utils.error(str(e))
		return 1
	except Exception as e:
		raise
	return 0

if __name__ == '__main__':
	exit(main())
