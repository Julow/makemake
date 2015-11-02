# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    module_printer.py                                  :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: juloo <juloo@student.42.fr>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/02 00:29:40 by juloo             #+#    #+#              #
#    Updated: 2015/11/02 12:52:32 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import config
import tempfile
import os
import json

HTML_FILE = """<!DOCTYPE html>
<html>
<head>
	<title>makemake2</title>
	<style type="text/css">

body
{
	margin: 0;
}
canvas
{
	display: block;
}

	</style>
</head>
<body>
	<script type="text/javascript">

drawer = (function(modules){

var BORDER_MARGIN = 15;
var MODULE_WIDTH = 100;
var MODULE_HEIGHT = 30;
var MODULE_MARGIN_H = 35;
var MODULE_MARGIN_V = 60;
var MODULE_BORDER_WIDTH = 1;
var MODULE_BORDER_COLOR = '#000000';
var MODULE_FILL_COLOR = '#FFFFFF';
var MODULE_TEXT_COLOR = '#000000';
var ARROW_HEAD_H = 3;
var ARROW_HEAD_V = 5;
var ARROW_WIDTH = 1;
var ARROW_COLOR = '#888888';
var MAX_SCALE = 2;

var modules_by_name = {};
var modules_by_height = {};
var max_height = -1;

function for_each(array, func)
{
	for (var i = 0; i < array.length; i++)
		func(array[i]);
}

for_each(modules, function(m)
{
	modules_by_name[m["name"]] = m;
	if (m["height"] > max_height)
		max_height = m["height"];
	if (!modules_by_height[m["height"]])
		modules_by_height[m["height"]] = [];
	modules_by_height[m["height"]].push(m);
});

var graph_width = 0;
var graph_height = (max_height + 2) * (MODULE_HEIGHT + MODULE_MARGIN_V) - MODULE_MARGIN_V; // lol

for (var i = 0; i <= max_height; i++)
	if (graph_width < modules_by_height[i].length)
		graph_width = modules_by_height[i].length;
graph_width = graph_width * (MODULE_WIDTH + MODULE_MARGIN_H) - MODULE_MARGIN_H;

var scale, offsetX, offsetY;

var canvas_node = document.createElement("canvas");
canvas_node.addEventListener("mousemove", check_cursor);
var canvas = canvas_node.getContext("2d");
document.body.appendChild(canvas_node);

var selected_module;

function check_winsize()
{
	var w = window.innerWidth;
	var h = window.innerHeight;

	canvas_node.width = w;
	canvas_node.height = h;
	scale = Math.min(MAX_SCALE, w / (BORDER_MARGIN * 2 + graph_width), h / (BORDER_MARGIN * 2 + graph_height));
	offsetX = (w / scale - graph_width) / 2;
	offsetY = (h / scale - graph_height) / 2;
	canvas.scale(scale, scale);
	update_modules_pos();
	draw();
}

function check_cursor(e)
{
	var x = e.offsetX / scale;
	var y = e.offsetY / scale;
	var old = selected_module;

	selected_module = null;
	for_each(modules, function(module)
	{
		var m_x = module["x"];
		var m_y = module["y"];

		if (x >= m_x && x < (m_x + MODULE_WIDTH)
			&& y >= m_y && y < (m_y + MODULE_HEIGHT))
			selected_module = module;
	});
	if ((old && selected_module && old["name"] == selected_module["name"]))
		return ;
	draw();
}

function update_modules_pos()
{
	var y = Math.ceil((graph_height - ((MODULE_HEIGHT + MODULE_MARGIN_V) * (max_height + 1) - MODULE_MARGIN_V)) / 2 + offsetY);
	var x, modules, height, i;

	for (height = max_height; height >= 0; height--)
	{
		modules = modules_by_height[height];
		x = Math.ceil((graph_width - (modules.length * (MODULE_WIDTH + MODULE_MARGIN_H) - MODULE_MARGIN_H)) / 2 + offsetX);
		for (i = 0; i < modules.length; i++)
		{
			modules[i]["x"] = x;
			modules[i]["y"] = y;
			x += MODULE_WIDTH + MODULE_MARGIN_H;
		}
		y += MODULE_HEIGHT + MODULE_MARGIN_V;
	}
}

function draw_arrows(module)
{
	var x = module["x"] + (MODULE_WIDTH / 2);
	var y = module["y"] + (MODULE_HEIGHT / 2);
	var center_y = MODULE_HEIGHT / 2;

	canvas.lineWidth = ARROW_WIDTH;
	canvas.strokeStyle = ARROW_COLOR;
	for_each(module["dep"], function(dep_name)
	{
		var dep = modules_by_name[dep_name];
		var dep_x = dep["x"] + (MODULE_WIDTH / 2);
		var dep_y = dep["y"] + center_y;
		var dist = (y - dep_y);

		dist /= dist / (MODULE_HEIGHT + MODULE_MARGIN_V);
		canvas.beginPath();
		canvas.moveTo(dep_x, dep_y + center_y);
		canvas.bezierCurveTo(dep_x, dep_y + dist, x, y - dist, x, y - center_y);
		canvas.moveTo(dep_x, dep_y + center_y);
		canvas.lineTo(dep_x - ARROW_HEAD_H, dep_y + ARROW_HEAD_V + center_y);
		canvas.moveTo(dep_x, dep_y + center_y);
		canvas.lineTo(dep_x + ARROW_HEAD_H, dep_y + ARROW_HEAD_V + center_y);
		canvas.stroke();
	});
}

function draw_modules()
{
	var module, x, y, i;

	canvas.textAlign = "center";
	canvas.lineJoin = "round";
	for (i = 0; i < modules.length; i++)
	{
		module = modules[i];
		x = module["x"];
		y = module["y"];
		canvas.fillStyle = MODULE_FILL_COLOR;
		canvas.fillRect(x, y, MODULE_WIDTH, MODULE_HEIGHT);
		canvas.strokeStyle = MODULE_BORDER_COLOR;
		canvas.lineWidth = MODULE_BORDER_WIDTH;
		canvas.strokeRect(x, y, MODULE_WIDTH, MODULE_HEIGHT);
		canvas.fillStyle = MODULE_TEXT_COLOR;
		canvas.fillText(modules[i]["name"], MODULE_WIDTH / 2 + x, MODULE_HEIGHT / 2 + y);
	}
}

function draw()
{
	canvas.clearRect(offsetX, offsetY, graph_width, graph_height);
	draw_modules();
	if (selected_module)
		draw_arrows(selected_module);
}

window.addEventListener("resize", check_winsize);
check_winsize();

}([
//?modules?
]));

	</script>
</body>
</html>
"""

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
		f.write(HTML_FILE.replace("//?modules?", json.dumps(module_data.values())))
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
