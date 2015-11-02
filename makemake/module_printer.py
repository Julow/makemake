# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_printer.py                                  :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/02 00:29:40 by juloo             #+#    #+#              #
#    Updated: 2015/11/02 01:12:15 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config
import tempfile
import os
import pkg_resources

#
# Generate an HTML file that render modules
# Return file name
#
def gen(modules):
	height_map = {}
	for m in modules:
		height_map[m] = -1
	for m in modules:
		if height_map[m] < 0:
			_set_height(height_map, m, 0)
	# TODO: check arrows direction
	tmp_f, tmp_file = tempfile.mkstemp(".html", "makemake_")
	with os.fdopen(tmp_f, "w") as f:
		f.write(pkg_resources.resource_string("makemake", config.HTML_FILE).replace(
			config.HTML_REPLACE, ",\n".join(["""\t{
		"name": "%(name)s",
		"dep": [%(dep)s],
		"height": %(height)d
	}""" % {
		"name": m.name,
		"dep": ", ".join(['"%s"' % dep.name for dep in m.public_required + m.private_required]),
		"height": height_map[m]
	} for m in modules])))
	return tmp_file

# Used to sort modules by dependency level
def _set_height(height_map, module, h):
	height_map[module] = h
	def loop(l):
		for m in l:
			if height_map[m] <= h:
				_set_height(height_map, m, h + 1)
	loop(module.public_required)
	loop(module.private_required)
