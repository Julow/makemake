# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    __main__.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 09:22:52 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/15 16:34:07 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from sys import argv
import module_searcher
import source_finder
import config
import os

#
# makemake2 [command]
#
# Available commands:
#  list					# Print a list of modules
#  check				# Check for error
#  help					# Print help
#

class ArgError(Exception):

	def __init__(self, err):
		self.err = err

	def __str__(self):
		return self.err

def list_command(args):
	modules = module_searcher.all()
	if len(modules) == 0:
		print "No module found"
	else:
		print "%d modules:" % len(modules)
		max_len = 0
		for m in modules:
			if len(m.module_name) > max_len:
				max_len = len(m.module_name)
		for m in modules:
			print "\t%-*s (%s)" % (max_len, m.module_name, os.path.relpath(m.base_dir))

def check_command(args):
	modules = module_searcher.load()
	if len(modules) == 0:
		print "No module found"
	else:
		print "%d modules - OK" % len(modules)

HELP = {
	"list": "Search and list all modules",
	"check": "Search modules and check for error",
	"help": "Show help about a command"
}

def help_command(args):
	if len(args) == 0:
		print "Commands:"
		for cmd in HELP:
			print "\t%-12s %s" % (cmd, HELP[cmd])
	else:
		for arg in args:
			if arg in HELP:
				print "\t%-12s %s" % (arg, HELP[arg])
			else:
				print "No help for '%s'" % arg

def def_command(args):
	absolute = True if len(args) > 0 and args[0] == "abs" else False
	modules = module_searcher.all()
	for m in modules:
		print "module %s: %s" % (m.module_name, m.base_dir if absolute else os.path.relpath(m.base_dir))
		for i in m.include_dirs:
			print "\tinclude %s" % (i if absolute else os.path.relpath(m.base_dir))
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
		for r in m.defaultRecipes:
			print "\trecipe %s" % r
		for t in m.targets:
			print "\ttarget %s" % t[0]
			for r in t[1]:
				print "\trecipe %s" % r
		print ""

# tmp START

def get_module(module_list, name):
	for m in module_list:
		if m.module_name == name:
			return m
	return None

def module_get_dirs(module_list, module, private = True):
	if module == None:
		print "INCLUDE LOOP"
		return []
	dirs = [module.base_dir] + module.include_dirs
	module_list = list(module_list)
	module_list.remove(module)
	for r in module.public_required:
		for d in module_get_dirs(module_list, get_module(module_list, r), False):
			if not d in dirs:
				dirs.append(d)
	if private:
		for r in module.private_required:
			for d in module_get_dirs(module_list, get_module(module_list, r), False):
				if not d in dirs:
					dirs.append(d)
	return dirs

# tmp END

def debug_command(args):
	modules = module_searcher.load()
	if len(modules) == 0:
		print "No module found"
	else:
		for m in modules:
			if not m.auto_enabled:
				continue
			print "MODULE %s:" % m.module_name
			sources = source_finder.track(m.base_dir, module_get_dirs(modules, m))
			for src in sources:
				includes = []
				for i in sources[src]:
					includes.append(os.path.relpath(i))
				print "\t%20s: %s" % (os.path.basename(src), ", ".join(includes))

COMMANDS = {
	"list": list_command,
	"check": check_command,
	"help": help_command,
	"def": def_command,
	"debug": debug_command,
}

def main():
	try:
		if len(argv) > 1:
			if argv[1] in COMMANDS:
				COMMANDS[argv[1]](argv[2:])
			else:
				raise ArgError("Unknow command '%s'" % command)
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
