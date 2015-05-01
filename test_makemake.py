#!/usr/bin/python
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test_makemake.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/05/01 23:15:55 by juloo             #+#    #+#              #
#    Updated: 2015/05/02 01:28:34 by juloo            ###   ########.fr        #
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

variables = {
	"NAME": ("", "$(NAME)"),

	"C_DIR": (".", "Sources directory"),
	"H_DIRS": (".", "Includes directories"),
	"O_DIR": ("o", "Obj directory"),

	"LIBS": ("", "Makefiles to call"),

	"C_FLAGS": ("-Wall -Wextra -Werror -O2", "Clang flags"),
	"CPP_FLAGS": ("-Wall -Wextra -Werror -O2", "Clang++ flags"),
	"NASM_FLAGS": ("-Wall -Werror", "Nasm flags"),

	"C_LINKS": ("", "Clang linking flags"),
	"CPP_LINKS": ("", "Clang++ linking flags"),
	"NASM_LINKS": ("", "Nasm linking flags"),

	"C_HEADS": ("", "Clang include flags"),
	"CPP_HEADS": ("", "Clang++ include flags"),
	"NASM_HEADS": ("", "Nasm include flags")
};

extensions = [
	(".cpp", "clang++"),
	(".c", "clang"),
	(".S", "nasm"),
	(".s", "nasm")
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

	def _dependencies(self, name):
		try:
			f = open(name, "r")
		except:
			return ""
		dep = ""
		for line in f:
			m = regInclude.match(line)
			if m != None:
				dep += " %s" % m.group(1)
		f.close()
		return dep

	def _createFileRules(self, output):
		cmd = Popen(["find", self.getVar("C_DIR", output), "-type", "f", "-print"], stdout=PIPE)
		for f in cmd.communicate():
			if f == None:
				continue
			for e in extensions:
				if f.endswith(e[0]):
					f.replace(e[0], ".o")
					output.write("""
%s:%s
	$(MSG_0) $< ; %s $(FLAGS) $(HEADS) -c -o $@ $< || $(MSG_1) $<
""" % (f, self._dependencies(f), e[1]))
					if len(f) > self.maxLen:
						self.maxLen = len(f)
					self.oFiles.append("%s\n" % f)
					oDir = "%s/%s" % (self.getVar("O_DIR", output), f)
					if not oDir in self.oDirs:
						self.oDirs.append(oDir)
					break

	def _createLibsRules(self, output):
		for lib in self.getVar("LIBS", output).split():
			self.phony.append(lib)
			f.write("""
%(0)s:
	@make -C %(0)s
""" % (lib))

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
		self.getVar("FLAGS", output)
		self.getVar("HEADS", output)
		self.getVar("LINKS", output)
		output.write("""
MSG_0 := printf '\\033[0;32m%%-%(maxlen)s.%(maxlen)ss\\033[0;0m\\r'
MSG_1 := printf '\\033[0;31m%%-%(maxlen)s.%(maxlen)ss\\033[0;0m\\n'

O_FILES := %(ofiles)s

$(NAME): %(odirs)s $(O_FILES)
	@$(MSG_0) $@ ; $(CC) $(FLAGS) -o $@ $(O_FILES) $(LINKS) && echo || $(MSG_1) $@

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
	"ofiles": "\n".join(self.oFiles),
	"odirs": " ".join(self.oDirs),
	"phony": " ".join(self.phony)
})
		output.close()

def main():
	makefile = Makefile("Makefile")
	makefile.build("Makefile")

main()
