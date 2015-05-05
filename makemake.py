#!/usr/bin/python
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    makemake.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/05/01 23:15:55 by juloo             #+#    #+#              #
#    Updated: 2015/05/05 13:17:19 by jaguillo         ###   ########.fr        #
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
from os import path
from collections import OrderedDict
from sys import argv, stdout
from fcntl import ioctl
from termios import TIOCSTI

variables = OrderedDict([
	("NAME", ("", "Project name")),

	("DIRS", (".", "Project directories")),
	("O_DIR", ("o", "Obj directory")),

	("LIBS", ("", "Makefiles to call")),

	("THREADS", ("1", "Number of threads")),

	("C_CC", ("clang", "C compiler")),
	("CPP_CC", ("clang++", "Cpp compiler")),
	("ASM_CC", ("nasm", "Asm compiler")),

	("LD_CC", ("", "Linking compiler")),

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

regVar = compile('^\s*(\w+)\s*[:]?=\s*(.*)$')
regInclude = compile('^\s*#\s*include\s*[<"]([^">]+)[">]\s*$')

class Rule():

	name = None
	dependencies = None
	content = None
	phony = False

	def __init__(self, name, dep = [], content = None, phony = False):
		self.name = name
		self.dependencies = dep
		self.content = content
		self.phony = phony

	def write(self, output):
		output.write("\n%s:" % self.name)
		for d in self.dependencies:
			output.write(" %s" % d)
		output.write("\n")
		if self.content != None:
			for l in self.content.split("\n"):
				output.write("\t@%s\n" % l)
		if self.phony:
			output.write(".PHONY: %s\n" % self.name)

class Makefile():

	var = None
	sources = None
	headers = None

	rules = None

	def __init__(self):
		self.var = {}
		self.sources = {}
		self.headers = []
		self.rules = []

#
# Variables
#

	def parse(self, name):
		try:
			f = open(name, "r")
		except:
			return
		for line in f:
			m = regVar.match(line)
			if m != None and m.group(1) in variables:
				self.var[m.group(1)] = m.group(2)
		f.close()

	def setVar(self, name, data):
		self.var[name] = data

	def getVar(self, name):
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
			self.setVar(name, data)
			return data
		return ""

#
# Files
#

	def findFiles(self):
		cmd_line = "find %s -type f -print" % self.getVar("DIRS")
		cmd = Popen(cmd_line.split(), stdout=PIPE)
		for f in cmd.stdout:
			f = path.split(f[:-1])
			if f[1].endswith(".h") or f[1].endswith(".hpp"):
				self.headers.append(f)
			else:
				e = self._extension(f)
				if e != None:
					self.sources[f] = (f[0], f[1][::-1].replace(e[0][::-1], "o.")[::-1])

	def _extension(self, source):
		for e in extensions:
			if source[1].endswith(e[0]):
				return e
		return None

	def _includes(self, source):
		try:
			f = open(source, "r")
		except:
			return []
		dep = []
		for line in f:
			m = regInclude.match(line)
			if m != None:
				for h in self.headers:
					if h[1] == m.group(1):
						dep.append("%s/%s" % h)
		f.close()
		return dep

#
# Build rules
#

	def _buildRuleAll(self):
		threads = self.getVar("THREADS")
		try:
			n = int(threads)
			if n <= 0:
				raise
		except:
			print("\033[31mWarning: $(THREADS) must be a valid positive non-null integer\033[0m")
			n = 1
			self.setVar("THREADS", "1")
		if n > 1:
			self.rules.insert(0, Rule("all", ["$(LIBS)"], "make -j$(THREADS) $(NAME)", True))
		else:
			self.rules.insert(0, Rule("all", ["$(LIBS)", "$(NAME)"], None, True))

	def _buildRuleOther(self):
		dirs = []
		o_dir = self.getVar("O_DIR")
		for s in self.sources:
			o = "%s/%s" % (o_dir, self.sources[s][0])
			if o in dirs:
				continue
			dirs.append(o)
		self.rules.append(Rule("clean", [], "rm -f $(O_FILES) 2> /dev/null || true\nrmdir -p %s $(O_DIR) 2> /dev/null || true" % " ".join(sorted(dirs, reverse=True)), True))
		self.rules.append(Rule("fclean", ["clean"], "rm -f $(NAME)", True))
		self.rules.append(Rule("re", ["fclean", "all"], None, True))
		self.rules.append(Rule("make", ["fclean"], "python makemake.py", True))

	def _buildRuleNAME(self):
		if not "LD_CC" in self.var:
			ld_cc = ""
			for e in extensions:
				if e[1] + "_CC" in self.var:
					ld_cc = self.var[e[1] + "_CC"]
					break
			if ld_cc == None:
				print("\033[31mWarning: Nothing to compile\033[0m")
			self.setVar("LD_CC", ld_cc)
		self.getVar("LD_FLAGS")
		self.rules.insert(0, Rule("$(NAME)", ["$(O_FILES)"],
			"$(MSG_0) $@ ; $(LD_CC) -o $@ $(O_FILES) $(LD_FLAGS) && echo || $(MSG_1) $@"))

	def _buildRuleSources(self):
		o_files = []
		o_dir = self.getVar("O_DIR")
		for s in self.sources:
			e = self._extension(s)
			o = "%s/%s/%s" % (o_dir, self.sources[s][0], self.sources[s][1])
			o_files.append(o)
			source = "%s/%s" % s
			dep = [source]
			dep += self._includes(source)
			self.rules.append(Rule(o, dep,
				"mkdir -p %(o_dir)s 2> /dev/null || true\n$(MSG_0) $< ; %(cc)s $(%(flags)s) $(%(heads)s) -c -o $@ $< || ($(MSG_1) $< && false)" % {
					"o_dir": "%s/%s" % (o_dir, self.sources[s][0]),
					"cc": self.getVar("%s_CC" % e[1]),
					"flags": "%s_FLAGS" % e[1],
					"heads": "%s_HEADS" % e[1]
				}))
			self.getVar("%s_FLAGS" % e[1])
			self.getVar("%s_HEADS" % e[1])
		self.setVar("O_FILES", " \\\n\t".join(o_files))

	def _buildRuleHeaders(self):
		for h in self.headers:
			header = "%s/%s" % h
			dep = self._includes(header)
			if len(dep) <= 0:
				continue
			self.rules.append(Rule(header, dep))

	def _buildRuleLibs(self):
		self.rules.append(Rule("$(LIBS)", [], "make -C $@", True))

	def build(self):
		self._buildRuleSources()
		self._buildRuleHeaders()
		self._buildRuleLibs()
		self._buildRuleNAME()
		self._buildRuleAll()
		self._buildRuleOther()
		self.rules.insert(0, Rule(".SILENT"))

#
# Write Makefile
#

	def _writeVars(self, output):
		output.write("\n#\n# Config\n#\n")
		for v in variables:
			if v in self.var:
				if variables[v][1] != None:
					output.write("\n# %s" % variables[v][1])
				output.write("\n%s := %s\n" % (v, self.var[v]))
		output.write("\n#\n# Internal\n#\n")
		for v in self.var:
			if not v in variables:
				output.write("\n%s := %s\n" % (v, self.var[v]))

	def _writeRules(self, output):
		for r in self.rules:
			r.write(output)

	def _writeBody(self, output):
		m = 0
		for r in self.rules:
			if len(r.name) > m:
				m = len(r.name)
		output.write("\nMSG_0 := printf '\\033[0;32m%%-%(maxlen)d.%(maxlen)ds\\033[0;0m\\r'\n" %
			{"maxlen": m})
		output.write("MSG_1 := printf '\\033[0;31m%%-%(maxlen)d.%(maxlen)ds\\033[0;0m\\n'\n" %
			{"maxlen": m})

	def write(self, name):
		try:
			output = open(name, "w")
		except:
			return
		output.write("#\n# %s\n#\n" % self.getVar("NAME"))
		output.write("# %s\n#\n" % name)
		self._writeVars(output)
		self._writeBody(output)
		self._writeRules(output)
		output.close()

makefile = Makefile()
makefile.parse("Makefile")
makefile.getVar("NAME")
makefile.findFiles()
makefile.build()
makefile.write("Makefile")
