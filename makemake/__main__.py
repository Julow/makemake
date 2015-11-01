# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    __main__.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 09:22:52 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/01 15:32:29 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from sys import argv, stdout
import module_searcher
import dependency_finder
import depend_generator
import makefile_generator
import module
import config
import os

#
# makemake2 [command]
#

#
# TODO:
# ?path? for full relative path (in module file)
# public local instruction
# override default recipe (possible ??)
#

def list_command(args):
	modules = module_searcher.all()
	if len(modules) == 0:
		print "No module found"
	else:
		print "%d modules:" % len(modules)
		max_len = 0
		for m in modules:
			if len(m.name) > max_len:
				max_len = len(m.name)
		for m in modules:
			print "\t%-*s (%s)" % (max_len, m.name, os.path.relpath(m.base_dir))

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
		for m in args:
			if module.get_module(modules, m) == None:
				raise config.BaseError("Unknow module '%s'" % m) # TODO: exception
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
			print "\tpublic require %s" % r.name
		for r in m.private_required:
			print "\tprivate require %s" % r.name
		for p in m.to_put:
			print "\tput %s %s" % (p, " ".join(m.to_put[p]))
		for l in m.locals:
			print "\tlocal %s" % l
		if not m.auto_enabled:
			print "\tdisable auto"
		for r in m.defaultRecipes:
			print "\trecipe %s" % r
		for t in m.targets:
			print "\ttarget %s" % t[0]
			for r in t[1]:
				print "\trecipe %s" % r
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
		for m in args:
			tmp = module.get_module(modules, m)
			if tmp == None:
				raise config.BaseError("Unknow module '%s'" % m) # TODO: exception
			if tmp in source_map:
				show_dep(tmp, source_map[tmp])
			else:
				raise config.BaseError("WTF happen with module '%s'" % m)

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

# print command
def set_height(height_map, module, h):
	height_map[module] = h
	def loop(l):
		for m in l:
			if height_map[m] >= h:
				set_height(height_map, m, h + 1)
	loop(module.public_required)
	loop(module.private_required)

def print_command(args):
	modules = module_searcher.load()
	height_map = {}
	for m in modules:
		height_map[m] = -1
	for m in modules:
		if height_map[m] < 0:
			set_height(height_map, m, 0)
	# TODO: check arrows direction
	by_height = {}
	for m in modules:
		if not height_map[m] in by_height:
			by_height[height_map[m]] = []
		by_height[height_map[m]].append(m)
	for h in sorted(by_height, reverse=True):
		print "%d: %s" % (h, " ".join([m.name for m in by_height[h]]))

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
		if len(argv) > 1:
			if argv[1] in COMMANDS:
				try:
					COMMANDS[argv[1]](argv[2:])
				except config.BaseError as e:
					raise config.BaseError("%s: %s" % (argv[1], str(e)))
			else:
				raise config.BaseError("Unknow command '%s'" % argv[1]) # TODO: exception
		else:
			print "%s: Available commands: %s" % (argv[0], ", ".join(sorted(COMMANDS.keys())))
			print "Type '%s help' for help" % argv[0]
			return 2
	except config.BaseError as e:
		print "%s: Error: %s" % (argv[0], str(e))
		return 1
	except Exception as e:
		raise
	return 0

if __name__ == '__main__':
	exit(main())