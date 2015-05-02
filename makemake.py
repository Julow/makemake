#!/usr/bin/python
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    makemake.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/05/01 23:15:55 by juloo             #+#    #+#              #
#    Updated: 2015/05/03 00:15:40 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#
# makemake.py
#
# Makefile generator
#
# Usage:
#  just run like: './makemake.py'
#

from re import compile
from subprocess import Popen, PIPE
from os.path import isfile
from collections import OrderedDict
from sys import argv, stdout
from fcntl import ioctl
from termios import TIOCSTI

variables = OrderedDict([
	("NAME", ("", "Executable name")),

	("C_DIR", (".", "Sources directory")),
	("H_DIRS", (".", "Includes directories")),
	("O_DIR", ("o", "Obj directory")),

	("LIBS", ("", "Makefiles to call")),

	("THREADS", ("1", "Number of threads")),

	("C_CC", ("clang", "C compiler")),
	("CPP_CC", ("clang++", "Cpp compiler")),
	("ASM_CC", ("nasm", "Asm compiler")),

	("C_FLAGS", ("-Wall -Wextra -Werror -O2", "Clang flags")),
	("CPP_FLAGS", ("-Wall -Wextra -Werror -O2", "Clang++ flags")),
	("ASM_FLAGS", ("-Wall -Werror", "Nasm flags")),

	("LD_FLAGS", ("", "Linking flags")),

	("C_HEADS", ("", "Clang include flags")),
	("CPP_HEADS", ("", "Clang++ include flags")),
	("ASM_HEADS", ("", "Nasm include flags"))
]);

extensions = [
	(".cpp", "CPP"),
	(".c", "C"),
	(".S", "ASM"),
	(".s", "ASM")
]

topTemplate = """#
# Makemake
#

"""

cRuleTemplate = """
%(rule)s: %(source)s %(odir)s%(dependencies)s
	@$(MSG_0) $< ; %(cc)s $(%(flags)s) $(%(heads)s) -c -o $@ $< || ($(MSG_1) $< && false)
"""

libRuleTemplate = """
%(lib)s:
	@make -C %(lib)s
.PHONY: %(lib)s
"""

bodyTemplate = """
$(NAME): $(LIBS) $(O_FILES)
	@$(MSG_0) $@ ; ld -o $@ $(O_FILES) $(LD_FLAGS) && echo || $(MSG_1) $@

$(O_DIR)/:
	@mkdir -p $@ 2> /dev/null || true

$(O_DIR)/%%:
	@mkdir -p $@ 2> /dev/null || true

clean:
	@rm -f $(O_FILES) 2> /dev/null || true
	@rmdir -p $(O_DIR) 2> /dev/null || true

fclean: clean
	@rm -f $(NAME) 2> /dev/null || true

re: fclean all

make:
	@python %s

.PHONY: all clean fclean re make
"""

regVar = compile('^\s*(\w+)\s*[:]?=\s*(.*)$')
regInclude = compile('^\s*#\s*include\s*"([^"]+)"\s*$')

class Makefile():

	var = None
	maxLen = 0
	oFiles = None
	oDirs = None

	def __init__(self, name):
		self.var = {}
		self.maxLen = 0
		self.oFiles = []
		self.oDirs = []
		self._parse(name)

	def setVar(self, name, data):
		self.var[name] = data

	def getVar(self, name, output):
		if name in self.var:
			return self.var[name]
		if name in variables:
			if variables[name][1] == None:
				data = variables[name][0]
			else:
				stdout.write("\033[33m%s:\033[39m " % variables[name][1])
				stdout.flush()
				for c in variables[name][0]:
					ioctl(0, TIOCSTI, c)
				data = raw_input()
			data.strip()
			if len(data) <= 0:
				data = variables[name][0]
			self.setVar(name, data)
			if variables[name][1] == None:
				output.write("\n%s := %s\n" % (name, data))
			else:
				output.write("\n# %s\n%s := %s\n" % (variables[name][1], name, data))
			return data
		return ""

	def _parse(self, name):
		try:
			f = open(name, "r")
		except:
			return
		for line in f:
			m = regVar.match(line)
			if m != None and m.group(1) in variables:
				self.setVar(m.group(1), m.group(2))
		f.close()

	def _createVariables(self, output):
		for v in variables:
			if v in self.var:
				if variables[v][1] != None:
					output.write("# %s\n" % variables[v][1])
				else:
					output.write("#\n")
				output.write("%s := %s\n" % (v, self.var[v]))

	def _createIntervalVars(self, output):
		output.write("\nMSG_0 := printf '\\033[0;32m%%-%(maxlen)d.%(maxlen)ds\\033[0;0m\\r'\n" %
			{"maxlen": self.maxLen})
		output.write("MSG_1 := printf '\\033[0;31m%%-%(maxlen)d.%(maxlen)ds\\033[0;0m\\n'\n" %
			{"maxlen": self.maxLen})
		space = False
		for v in self.var:
			if not v in variables:
				if not space:
					space = True
					output.write("\n")
				output.write("%s := %s\n" % (v, self.var[v]))
		output.write("\nO_FILES :=	%s\n" % " \\\n\t\t\t".join(self.oFiles))

	def _dependencies(self, name, hDirs):
		try:
			f = open(name, "r")
		except:
			return ""
		dep = ""
		for line in f:
			m = regInclude.match(line)
			if m != None:
				for d in hDirs:
					h = "%s/%s" % (d, m.group(1))
					if isfile(h):
						dep += " %s" % h
		f.close()
		return dep

	def _createFileRules(self, output):
		cmd = Popen(["find", self.getVar("C_DIR", output), "-type", "f", "-print"], stdout=PIPE)
		for f in cmd.stdout:
			f = f[:-1]
			for e in extensions:
				if f.endswith(e[0]):
					o = f.replace(e[0], ".o")
					varFlags = "%s_FLAGS" % e[1]
					varHeads = "%s_HEADS" % e[1]
					self.getVar(varFlags, output)
					self.getVar(varHeads, output)
					oDir = self.getVar("O_DIR", output)
					cDir = self.getVar("C_DIR", output)
					output.write(cRuleTemplate % {
						"rule": o,
						"source": f,
						"dependencies": self._dependencies(f, self.getVar("H_DIRS", output).split()),
						"cc": self.getVar("%s_CC" % e[1], output),
						"flags": varFlags,
						"heads": varHeads,
						"odir": "%s/%s" % (oDir, "/".join(o.replace(cDir + "/", '').split('/')[:-1]))
					})
					if len(o) > self.maxLen:
						self.maxLen = len(o)
					self.oFiles.append(o)

	def _createAllRule(self, output):
		threadsVar = self.getVar("THREADS", output)
		try:
			threads = int(threadsVar)
		except:
			threads = 1
			self.setVar("THREADS", 1)
		if threads <= 1:
			threads = 1
			output.write("\nall: $(NAME)\n")
		else:
			output.write("\nall:\n\t@make -j$(THREADS) $(NAME)\n")

	def _createLibsRules(self, output):
		for lib in self.getVar("LIBS", output).split():
			output.write(libRuleTemplate % {"lib": lib})

	def build(self, name):
		try:
			output = open(name, "w")
		except:
			return
		output.write(topTemplate)
		self._createVariables(output)
		self.getVar("NAME", output)
		self._createAllRule(output)
		self._createFileRules(output)
		self._createLibsRules(output)
		self.getVar("LD_FLAGS", output)
		self._createIntervalVars(output)
		output.write(bodyTemplate % argv[0])
		output.close()

makefile = Makefile("Makefile")
makefile.build("Makefile")
print("\033[32mMakefile ready\033[39m")
