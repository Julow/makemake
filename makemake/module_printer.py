# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_printer.py                                  :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/02 00:29:40 by juloo             #+#    #+#              #
#    Updated: 2015/11/19 00:34:08 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config
import tempfile
import os
import json
from module_print_html import HTML, MODULES_MARK

#
# Generate an HTML file that render modules
# Return file name
#
def gen(modules):
	height_map = {}
	for m in modules:
		height_map[m] = -1
	for m in modules:
		if m.is_main:
			_set_height(height_map, m, 0)
	max_height = 0
	for m in modules:
		if height_map[m] > max_height:
			max_height = height_map[m]
	for m in modules:
		if m.is_main:
			_raise_module(height_map, m, max_height)
			height_map[m] = 0
	module_data = {}
	for m in modules:
		module_data[m.name] = {
			"name": m.name,
			"dep": [dep.name for dep in m.public_required + m.private_required],
			"level": height_map[m]
		}
	tmp_f, tmp_file = tempfile.mkstemp(".html", "makemake_")
	with os.fdopen(tmp_f, "w") as f:
		f.write(HTML.replace(MODULES_MARK, json.dumps(module_data.values())))
	return tmp_file

# Sort modules in the graph by dependency level
def _set_height(height_map, module, h):
	height_map[module] = h
	def loop(l):
		for m in l:
			if height_map[m] <= h:
				_set_height(height_map, m, h + 1)
	loop(module.public_required)
	loop(module.private_required)

# Try to raise modules
def _raise_module(height_map, module, max_height):
	required = module.public_required + module.private_required
	min_height = max_height
	for m in required:
		_raise_module(height_map, m, max_height)
		if height_map[m] <= min_height:
			min_height = height_map[m] - 1
	if height_map[module] < min_height:
		height_map[module] = min_height
