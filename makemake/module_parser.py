# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_parser.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 08:53:32 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/05 00:19:33 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import module
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
#	public include include/				# Path to public headers dir (or file)
#
#	private include include/internal	# local HEAD_FLAGS += -Iinclude/internal
#	include templates					# Same
#
#	public require module1				# Declare a public dependency
#
#	private require module2				# Same but the dependency is private
#	require module3						# Default visibility is always 'private'
#
#	put LINK_FLAGS -lm					# Put (without dupplicate) '-lm'
#											to the variable LINK_FLAGS
#
#	local DEBUG_FLAGS += -DDEBUG		# Target only variable
#
#	disable auto						# Disable automatic search for source
#
#	makefile include file.mk			# Add an 'include file.mk' directive
#	makefile import file.mk				# Copy the content of file.mk
#
#									# The indentation is not important
#
# -
#

#

def _instruction_makefile(module, args, visibility):
	if not args[0] in ["include", "import"]:
		raise config.BaseError("Unknown action '%s'" % args[0])
	module.mk_import(args[1], args[0] == "import")

#

MODULE_INSTRUCTIONS = {
	"include":	(1, -1,	lambda m, w, v: m.include(w, v == "public")),
	"require":	(1, 1,	lambda m, w, v: m.require(w[0], v == "public")),
	"put":		(2, -1,	lambda m, w, v: m.put(w[0], w[1:])),
	"local":	(1, -1,	lambda m, w, v: m.local(" ".join(w))),
	"disable":	(1, 1,	lambda m, w, v: m.disable(w[0])),
	"makefile":	(2, 2,	_instruction_makefile)
}

class ParserError(config.BaseError):

	def __init__(self, err):
		super(ParserError, self).__init__(err)

#
# Parse a module file
#  and return a list of Module
#
# raise a ParserError on error
#

def parse(file_name):
	modules = []
	current_module = None
	line_n = 0
	f_line = ""
	try:
		with open(file_name, "r") as f:
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
						raise ParserError("What??" % visiblity)
				if words[0] == "module":
					if not len(words) in [2, 3]:
						raise ParserError("%s argument for 'module'" % ("Not enougth" if len(words) < 2 else "Too many"))
					if words[1].endswith(":"):
						words[1] = words[1][:-1]
					rel = os.path.relpath(words[2] if len(words) == 3 else ".")
					current_module = module.Module(words[1], os.path.abspath(os.path.join(os.path.dirname(file_name), rel)))
					modules.append(current_module)
				elif words[0] in MODULE_INSTRUCTIONS:
					instr = MODULE_INSTRUCTIONS[words[0]]
					args = words[1:]
					if instr[0] >= 0 and len(args) < instr[0]:
						raise ParserError("Not enougth argument for '%s'" % words[0])
					if instr[1] >= 0 and len(args) > instr[1]:
						raise ParserError("Too many argument for '%s'" % words[0])
					instr[2](current_module, args, visiblity)
				else:
					raise ParserError("Unknow instruction '%s'" % words[0])
	except ParserError as e:
		raise ParserError("%s at line %d in %s \"%s\"" % (str(e), line_n, os.path.relpath(file_name), f_line));
	except Exception as e:
		raise ParserError("Cannot open %s: %s" % (file_name, str(e)))
	return modules
