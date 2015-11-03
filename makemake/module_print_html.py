MODULES_MARK = "/* ?modules? */[]"
HTML = """<!DOCTYPE html>
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
var MODULE_MARGIN_H = 40;
var MODULE_MARGIN_V = 60;
var MODULE_BORDER_WIDTH = 1;
var MODULE_BORDER_COLOR = '#000000';
var MODULE_FILL_COLOR = '#FFFFFF';
var MODULE_TEXT_COLOR = '#000000';
var ARROW_BASE = 5;
var ARROW_HEAD_H = 3;
var ARROW_HEAD_V = 5;
var ARROW_WIDTH = 0.8;
var ARROW_COLOR = '#444444';
var DEP_ARROW_COLOR = '#D5D5D5';
var MAX_SCALE = 2;

var modules_by_name = {};
var modules_by_level = {};
var max_level = -1;

// begin lol
function for_each(array, func)
{
	for (var i = 0; i < array.length; i++)
		func(array[i]);
}

function contains(array, obj)
{
	for (var i = 0; i < array.length; i++)
		if (array[i] == obj)
			return (true);
	return (false);
}
// end lol

for_each(modules, function(m)
{
	modules_by_name[m["name"]] = m;
	if (m["level"] > max_level)
		max_level = m["level"];
	if (!modules_by_level[m["level"]])
		modules_by_level[m["level"]] = [];
	modules_by_level[m["level"]].push(m);
});

var graph_width = 0;
var graph_height = (max_level + 2) * (MODULE_HEIGHT + MODULE_MARGIN_V) - MODULE_MARGIN_V; // lol

for (var i = 0; i <= max_level; i++)
	if (graph_width < modules_by_level[i].length)
		graph_width = modules_by_level[i].length;
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
	var y = Math.ceil((graph_height - ((MODULE_HEIGHT + MODULE_MARGIN_V) * (max_level + 1) - MODULE_MARGIN_V)) / 2 + offsetY);
	var x, mods, level, i;

	for (level = max_level; level >= 0; level--)
	{
		mods = modules_by_level[level];
		x = Math.ceil((graph_width - (mods.length * (MODULE_WIDTH + MODULE_MARGIN_H) - MODULE_MARGIN_H)) / 2 + offsetX);
		for (i = 0; i < mods.length; i++)
		{
			mods[i]["x"] = x;
			mods[i]["y"] = y;
			x += MODULE_WIDTH + MODULE_MARGIN_H;
		}
		y += MODULE_HEIGHT + MODULE_MARGIN_V;
	}
}

function draw_arrow(from, to, color)
{
	var center_y = MODULE_HEIGHT / 2;
	var from_x = from["x"] + (MODULE_WIDTH / 2);
	var from_y = from["y"] + center_y;
	var to_x = to["x"] + (MODULE_WIDTH / 2);
	var to_y = to["y"] + center_y;
	var dist_y = from_y - to_y;

	dist_y /= dist_y / (MODULE_HEIGHT + MODULE_MARGIN_V);
	canvas.lineWidth = ARROW_WIDTH;
	canvas.fillStyle = color;
	canvas.strokeStyle = color;
	// base
	canvas.beginPath();
	canvas.moveTo(from_x, from_y - center_y);
	canvas.arc(from_x, from_y - center_y, ARROW_BASE / 2, 0, Math.PI * 2);
	canvas.fill();
	// curve
	canvas.moveTo(to_x, to_y + center_y);
	canvas.bezierCurveTo(to_x, to_y + dist_y, from_x, from_y - dist_y, from_x, from_y - center_y);
	// arrow
	canvas.moveTo(to_x, to_y + center_y);
	canvas.lineTo(to_x - ARROW_HEAD_H, to_y + ARROW_HEAD_V + center_y);
	canvas.moveTo(to_x, to_y + center_y);
	canvas.lineTo(to_x + ARROW_HEAD_H, to_y + ARROW_HEAD_V + center_y);
	canvas.stroke();
}

function draw_modules()
{
	var module, x, y, i;

	canvas.textAlign = "center";
	canvas.lineJoin = "round";
	for_each(modules, function(module)
	{
		x = module["x"];
		y = module["y"];
		canvas.fillStyle = MODULE_FILL_COLOR;
		canvas.fillRect(x, y, MODULE_WIDTH, MODULE_HEIGHT);
		canvas.strokeStyle = MODULE_BORDER_COLOR;
		canvas.lineWidth = MODULE_BORDER_WIDTH;
		canvas.strokeRect(x, y, MODULE_WIDTH, MODULE_HEIGHT);
		canvas.fillStyle = MODULE_TEXT_COLOR;
		canvas.fillText(module["name"], MODULE_WIDTH / 2 + x, MODULE_HEIGHT / 2 + y);
	});
}

function draw()
{
	canvas.clearRect(offsetX, offsetY, graph_width, graph_height);
	if (selected_module)
		for_each(modules, function(m)
		{
			if (contains(m["dep"], selected_module["name"]))
				draw_arrow(m, selected_module, DEP_ARROW_COLOR);
		});
	if (selected_module)
		for_each(selected_module["dep"], function(dep_name)
		{
			draw_arrow(selected_module, modules_by_name[dep_name], ARROW_COLOR);
		});
	draw_modules();
}

window.addEventListener("resize", check_winsize);
check_winsize();

}(""" + MODULES_MARK + """));

	</script>
</body>
</html>
"""
