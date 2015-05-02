#!/usr/bin/python
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test_makemake.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/05/01 23:15:55 by juloo             #+#    #+#              #
#    Updated: 2015/05/02 02:21:29 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#
# makemake.py
#
# <<Test>>
#
# Minimal project manager
#
# -
#

#
# TODO:
# Makefile generator
# Prompt for config
# Lib manager (libft, libftprintf, libftreg, libget_next_line, etc...)
# Dependencies
#

from re import compile
from subprocess import Popen, PIPE
from os.path import isfile

variables = {
	"NAME": ("", "$(NAME)"),

	"C_DIR": (".", "Sources directory"),
	"H_DIRS": (".", "Includes directories"),
	"O_DIR": ("o", "Obj directory"),

	"LIBS": ("", "Makefiles to call"),

	"CC_C": ("clang", ".c compilator"),
	"CC_CPP": ("clang++", ".cpp compilator"),
	"CC_ASM": ("nasm", ".s compilator"),

	"C_FLAGS": ("-Wall -Wextra -Werror -O2", "Clang flags"),
	"CPP_FLAGS": ("-Wall -Wextra -Werror -O2", "Clang++ flags"),
	"ASM_FLAGS": ("-Wall -Werror", "Nasm flags"),

	"LD_FLAGS": ("", "Linking flags"),

	"C_HEADS": ("", "Clang include flags"),
	"CPP_HEADS": ("", "Clang++ include flags"),
	"ASM_HEADS": ("", "Nasm include flags")
};

extensions = [
	(".cpp", "CPP"),
	(".c", "C"),
	(".S", "ASM"),
	(".s", "ASM")
]

regVar = compile('^\s*(\w+)\s*[:]?=\s*(.*)$')
regInclude = compile('^\s*#\s*include\s*"([^"]+)"\s*$')

class Makefile():

	var = None
	maxLen = 0
	oFiles = None
	oDirs = None
	phony = None

	def __init__(self, name):
		self.var = {}
		self.maxLen = 0
		self.oFiles = []
		self.oDirs = []
		self.phony = ["all", "clean", "fclean", "re", "make"]
		self._parse(name)

	def setVar(self, name, data):
		self.var[name] = data

	def getVar(self, name, output):
		if name in self.var:
			return self.var[name]
		if name in variables:
			if variables[name][1] == None:
				data = variables[name][0]
			elif variables[name][0] == "":
				data = raw_input("%s: " % variables[name][1])
			else:
				data = raw_input("%s (%s):" % (variables[name][1], variables[name][0]))
			data.strip()
			if len(data) <= 0:
				data = variables[name][0]
			self.setVar(name, data)
			output.write("%s := %s\n" % (name, data))
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
					output.write("""
%s: %s%s
	@$(MSG_0) $< ; %s $(%s) $(%s) -c -o $@ $< || $(MSG_1) $< && false
""" % (o, f, self._dependencies(f, self.getVar("H_DIRS", output).split()),
	self.getVar("CC_%s" % e[1], output), varFlags, varHeads))
					if len(o) > self.maxLen:
						self.maxLen = len(o)
					self.oFiles.append(o)
					oDir = "%s/%s" % (self.getVar("O_DIR", output), o)
					if not oDir in self.oDirs:
						self.oDirs.append(oDir)
					break

	def _createLibsRules(self, output):
		for lib in self.getVar("LIBS", output).split():
			self.phony.append(lib)
			output.write("""
%s:
	@make -C %s
""" % (lib, lib))

	def build(self, name):
		try:
			output = open(name, "w")
		except:
			return
		output.write("""
#
# Makemake
#

""")
		for v in self.var:
			output.write("%s := %s\n" % (v, self.var[v]))
		self.getVar("NAME", output)
		output.write("""
all: $(NAME)
""")
		self._createFileRules(output)
		self._createLibsRules(output)
		self.getVar("LD_FLAGS", output)
		output.write("""
MSG_0 := printf '\\033[0;32m%%-%(maxlen)s.%(maxlen)ss\\033[0;0m\\r'
MSG_1 := printf '\\033[0;31m%%-%(maxlen)s.%(maxlen)ss\\033[0;0m\\n'

O_FILES := %(ofiles)s

$(NAME): %(odirs)s $(O_FILES)
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

.PHONY: %(phony)s
""" % {
	"maxlen": self.maxLen,
	"ofiles": " \\\n\t".join(self.oFiles),
	"odirs": " ".join(self.oDirs),
	"phony": " ".join(self.phony)
})
		output.close()

def main():
	makefile = Makefile("Makefile")
	makefile.build("Makefile")

main()
