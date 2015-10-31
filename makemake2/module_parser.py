# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_parser.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 08:53:32 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/31 18:20:27 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
from module_def import ModuleDef
import config

#
# module file syntax
#
# module declaration goes to a 'module' file
# these files are searched recursively
#
# There can be several module declaration per file
#
# module module_name: base_dir		# Declare a module
#
#										base_dir is the base dir of the module
#										(default: current dir)
#
#									# Everything is optionnal
#
#	include include/					# path to public headers dir (or file)
#
#	public require module1				# Declare a public dependency
#
#	private require module2				# Same but the dependency is private
#	require module3						# Default visibility is 'private'
#
#	put LINK_FLAGS -lm					# Put (without dupplicate) '-lm'
#											to the variable LINK_FLAGS
#
#	local DEBUG_FLAGS += -DDEBUG		# Target only variable
#
#	disable auto						# Disable automatic search for source
#
#	target test.o: test.c test.h		# Add a target
#
#	recipe clang $^ -o $@				# Add a recipe to the target
#
#									# The indentation is not important
#
# -
#

MODULE_INSTRUCTIONS = {
	"include":	(1, -1,	lambda m, w, v: ModuleDef.include(m, w)),
	"require":	(1, 1,	lambda m, w, v: ModuleDef.require(m, w[0], v == "public")),
	"put":		(2, -1,	lambda m, w, v: ModuleDef.put(m, w[0], w[1:])),
	"local":	(1, -1,	lambda m, w, v: ModuleDef.local(m, " ".join(w))),
	"disable":	(1, 1,	lambda m, w, v: ModuleDef.disable(m, w[0])),
	"recipe":	(1, -1,	lambda m, w, v: ModuleDef.recipe(m, " ".join(w))),
	"target":	(1, -1,	lambda m, w, v: ModuleDef.target(m, " ".join(w)))
}

class ParserError(config.BaseError):

	def __init__(self, err):
		super(ParserError, self).__init__(err)

#
# Parse a module file
#  and return a list of ModuleDef
#
# raise a ParserError on error
#

def parse(file_name):
	modules = []
	current_module = None
	try:
		with open(file_name, "r") as f:
			line_n = 0
			for f_line in f:
				line_n += 1
				f_line = f_line.strip()
				if f_line.find("#") >= 0:
					line = f_line.split("#")[0].rstrip()
				else:
					line = f_line
				if len(line) == 0:
					continue
				words = line.split()
				visiblity = config.DEFAULT_VISIBILITY
				if words[0] in ["public", "private"]:
					visiblity = words[0]
					words = words[1:]
					if len(words) == 0:
						raise ParserError("Useless %s at line %d \"%s\"" % (visiblity, line_n, f_line))
				if words[0] == "module":
					if not len(words) in [2, 3]:
						raise ParserError("%s argument for 'module' at line %d \"%s\"" % (
							"Not enougth" if len(words) < 2 else "Too many",
							line_n, f_line
						))
					if words[1].endswith(":"):
						words[1] = words[1][:-1]
					rel = os.path.relpath(words[2] if len(words) == 3 else ".")
					current_module = ModuleDef(words[1], os.path.abspath(os.path.join(os.path.dirname(file_name), rel)))
					modules.append(current_module)
				elif words[0] in MODULE_INSTRUCTIONS:
					try:
						instr = MODULE_INSTRUCTIONS[words[0]]
						args = words[1:]
						if instr[0] >= 0 and len(args) < instr[0]:
							raise ParserError("Not enougth argument for '%s'" % words[0])
						if instr[1] >= 0 and len(args) > instr[1]:
							raise ParserError("Too many argument for '%s'" % words[0])
						instr[2](current_module, args, visiblity)
					except str as e:
						raise ParserError("%s at line %d \"%s\"" % (e, line_n, f_line))
				else:
					raise ParserError("Unknow instruction '%s' at line %d \"%s\"" % (words[0], line_n, f_line))
	except ParserError:
		raise
	except Exception as e:
		raise ParserError("Cannot open %s: %s" % (file_name, str(e)))
	return modules
