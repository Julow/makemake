#!/usr/bin/python
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    makemake.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/05/01 23:15:55 by juloo             #+#    #+#              #
#    Updated: 2015/08/03 19:33:47 by juloo            ###   ########.fr        #
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
from sys import argv, stdout, exit

try:
	from fcntl import ioctl
	from termios import TIOCSTI

	def ask_user(prompt = None, default = ""):
		if prompt != None:
			stdout.write(prompt)
			stdout.flush()
		for c in default:
			ioctl(0, TIOCSTI, c)
		return raw_input()

except ImportError:
	def ask_user(prompt = None, default = ""):
		if prompt != None:
			stdout.write(prompt)
		if len(default) > 0:
			stdout.write("(%s): " % default)
		stdout.flush()
		r = raw_input()
		if len(r) <= 0:
			return default
		return r

def includeSearch(make):
	dirs = []
	for h in make.files:
		if h.endswith(".h") or h.endswith(".hpp"):
			h = "-I %s" % path.dirname(h)
			if not h in dirs:
				dirs.append(h)
	return ' '.join(dirs)

def modulesSearch(make):
	modules = []
	cmd_line = "git submodule status"
	cmd = Popen(cmd_line.split(), stdout=PIPE)
	for l in cmd.stdout:
		m = l.split()
		if len(m) == 2:
			modules.append(m[1])
	return ' '.join(modules)

variables = OrderedDict([
	("NAME", ("", "Project name", None)),

	("DIRS", ("srcs include", "Project directories", None)),
	("O_DIR", ("o", "Obj directory", None)),

	("LIBS", ("", "Makefiles to call (directory)", None)),
	("MODULES", ("", "Modules to init (directory)", modulesSearch)),

	("THREADS", ("1", "Number of threads", None)),

	("C_CC", ("clang", "C compiler", None)),
	("CPP_CC", ("clang++", "C++ compiler", None)),
	("ASM_CC", ("nasm", "ASM compiler", None)),

	("LD_CC", ("", "Linking compiler", None)),

	("C_FLAGS", ("-Wall -Wextra -Werror -O2", "C flags", None)),
	("CPP_FLAGS", ("-Wall -Wextra -Werror -O2", "C++ flags", None)),
	("ASM_FLAGS", ("-Wall -Werror", "ASM flags", None)),

	("LD_FLAGS", ("", "Linking flags", None)),

	("C_HEADS", ("", "C include flags", includeSearch)),
	("CPP_HEADS", ("", "C++ include flags", includeSearch)),
	("ASM_HEADS", ("", "ASM include flags", includeSearch)),

	("NICE_OUTPUT", ("1", None, None))
]);

compilers = [
	(".cpp", "CPP", "clang++", "$(LD_CC) -o $@ $(O_FILES) $(LD_FLAGS)"),
	(".c", "C", "clang", "$(LD_CC) -o $@ $(O_FILES) $(LD_FLAGS)"),
	(".S", "ASM", "nasm", "$(LD_CC) $(LD_FLAGS) -o $@ $(O_FILES)"),
	(".s", "ASM", "nasm", "$(LD_CC) $(LD_FLAGS) -o $@ $(O_FILES)"),
	(None, "AR", "ar", "$(LD_CC) $(LD_FLAGS) $@ $(O_FILES)"),
	(None, None, None, "$(LD_CC) $(LD_FLAGS) $@ $(O_FILES)")
]

regVar = compile('^\s*(\w+)\s*[:]?=\s*(.*)$')
regInclude = compile('^\s*#\s*include\s*[<"]([^">]+)[">]\s*$')

modules_rule = "$(addsuffix /.git,$(MODULES))"

interactiveMode = True

class Rule():

	name = None
	dependencies = None
	content = None
	phony = False
	orderOnly = None

	def __init__(self, name, dep = [], content = None, phony = False, orderOnly = []):
		self.name = name
		self.dependencies = dep
		self.content = content
		self.phony = phony
		self.orderOnly = orderOnly

	def write(self, output):
		output.write("\n%s:" % self.name)
		for d in self.dependencies:
			output.write(" %s" % d)
		if len(self.orderOnly) > 0:
			output.write(" |")
			for d in self.orderOnly:
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
	files = None

	o_dirs = None

	rules = None

	def __init__(self):
		self.var = {}
		self.sources = {}
		self.files = []
		self.o_dirs = []
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
			if variables[name][1] == None or not interactiveMode:
				data = variables[name][0]
			else:
				if variables[name][2] != None:
					defVar = variables[name][2](self)
				else:
					defVar = variables[name][0]
				data = ask_user("\033[33m%s:\033[39m " % variables[name][1], defVar)
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
			f = f[:-1]
			e = self._compiler(f)
			if e != None:
				f = path.split(f)
				self.sources[f] = (f[0].replace("..", "_.."), f[1][::-1].replace(e[0][::-1], "o.")[::-1])
			else:
				self.files.append(f)

	def _compiler(self, source):
		for e in compilers:
			if e[0] != None and source.endswith(e[0]):
				return e
		return None

	def _includes(self, source, incs):
		try:
			f = open(source, "r")
		except:
			return []
		for line in f:
			m = regInclude.match(line)
			if m != None:
				for h in self.files:
					if h.endswith(m.group(1)):
						if h in incs:
							continue
						incs.append(h)
						self._includes(h, incs)
		f.close()
		return incs

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
			self.rules.insert(0, Rule("all", [modules_rule, "$(LIBS)"], "make -j$(THREADS) $(NAME)", True))
		else:
			self.rules.insert(0, Rule("all", [modules_rule, "$(LIBS)", "$(NAME)"], None, True))

	def _buildRuleOther(self):
		self.setVar("O_DIRS", ' '.join(sorted(self.o_dirs, reverse=True)))
		self.rules.append(Rule("$(O_DIRS)", [], "mkdir -p $@ 2> /dev/null || true"))
		self.rules.append(Rule("clean", [], "rm -f $(O_FILES) 2> /dev/null || true\nrmdir -p $(O_DIRS) $(O_DIR) 2> /dev/null || true", True))
		self.rules.append(Rule("fclean", ["clean"], "rm -f $(NAME)", True))
		self.rules.append(Rule("re", ["fclean", "all"], None, True))

	def _buildRuleNAME(self):
		if not "LD_CC" in self.var:
			ld_cc = None
			for e in compilers:
				if e[1] != None and e[1] + "_CC" in self.var:
					ld_cc = self.var[e[1] + "_CC"]
					break
			if ld_cc == None:
				print("\033[31mWarning: Nothing to compile\033[0m")
			self.setVar("LD_CC", ld_cc)
		else:
			ld_cc = self.getVar("LD_CC")
		ld_line = ""
		for e in compilers:
			if e[2] == ld_cc or e[2] == None:
				ld_line = e[3]
				break
		self.getVar("LD_FLAGS")
		self.rules.insert(0, Rule("$(NAME)", ["$(O_FILES)"],
			"$(MSG_0) $@ ; %s && $(MSG_END) || $(MSG_1) $@" % ld_line))

	def _buildRuleSources(self):
		o_files = []
		o_dir = self.getVar("O_DIR")
		for s in sorted(self.sources):
			e = self._compiler(s[1])
			o_path = "%s/%s" % (o_dir, self.sources[s][0])
			if not o_path in self.o_dirs:
				self.o_dirs.append(o_path)
			o = "%s/%s" % (o_path, self.sources[s][1])
			o_files.append(o)
			source = "%s/%s" % s
			dep = [source]
			dep += sorted(self._includes(source, []))
			self.rules.append(Rule(o, dep,
				"$(MSG_0) $< ; %(cc)s $(%(flags)s) $(%(heads)s) -c -o $@ $< || ($(MSG_1) $< && false)" % {
					"cc": self.getVar("%s_CC" % e[1]),
					"flags": "%s_FLAGS" % e[1],
					"heads": "%s_HEADS" % e[1]
				}, False, [o_path]))
			self.getVar("%s_FLAGS" % e[1])
			self.getVar("%s_HEADS" % e[1])
		self.setVar("O_FILES", " \\\n\t".join(o_files))

	def _buildRuleLibs(self):
		self.rules.append(Rule("$(LIBS)", [], "make -C $@", True))
		self.rules.append(Rule(modules_rule, [], "git submodule init $(@:.git=)\ngit submodule update $(@:.git=)", False))

	def build(self):
		self._buildRuleSources()
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
		if self.getVar("NICE_OUTPUT") == "0":
			output.write("\nMSG_0 := printf '\\033[0;32m%s\\033[0;0m\\n'\n")
			output.write("MSG_1 := printf '\\033[0;31m%s\\033[0;0m\\n'\n")
			output.write("MSG_END := true\n")
		else:
			maxlen = 0
			for r in self.rules:
				if len(r.name) > maxlen:
					maxlen = len(r.name)
			output.write("\nMSG_0 := printf '\\033[0;32m%%-%(maxlen)d.%(maxlen)ds\\033[0;0m\\r'\n" %
				{"maxlen": maxlen})
			output.write("MSG_1 := printf '\\033[0;31m%%-%(maxlen)d.%(maxlen)ds\\033[0;0m\\n'\n" %
				{"maxlen": maxlen})
			output.write("MSG_END := printf '\\n'\n")

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

if len(argv) > 1:
	if argv[1] == "--test":
		interactiveMode = False
	else:
		print("Makemake")
		print("Options:")
		print("  --test      Run")
		exit()

makefile = Makefile()
makefile.parse("Makefile")
makefile.getVar("NAME")
makefile.findFiles()
makefile.build()
makefile.getVar("LIBS")
makefile.getVar("MODULES")
makefile.write("Makefile")
