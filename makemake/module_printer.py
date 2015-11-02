# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_printer.py                                  :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/02 00:29:40 by juloo             #+#    #+#              #
#    Updated: 2015/11/02 22:54:35 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config
import tempfile
import os
import json

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
	module_data = {}
	for m in modules:
		module_data[m.name] = {
			"name": m.name,
			"dep": [dep.name for dep in m.public_required + m.private_required],
			"level": height_map[m]
		}
	tmp_f, tmp_file = tempfile.mkstemp(".html", "makemake_")
	with os.fdopen(tmp_f, "w") as f:
		f.write(config.cat_file('res/module_print.html').replace("//?modules?", json.dumps(module_data.values())))
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
