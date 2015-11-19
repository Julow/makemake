# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/03 09:35:59 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/19 16:50:20 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import webbrowser
import subprocess
import sys
import config
import time

# Open url in a browser
def open_browser(url):
	if sys.platform == 'darwin':
		subprocess.Popen(['open', url])
	else:
		webbrowser.open(url, 0, True)

# Substitute ?variables? in text
def substitute_vars(text, v):
	return config.VARIABLE_REG.sub(lambda m: v[m.group(1)] if m.group(1) in v else m.group(0), text)

def warn(msg):
	print "\033[33mWarning:\033[0m %s" % msg

def error(msg):
	print "\033[31mError:\033[0m %s" % msg

#
# Time
#

time_stack = []

time_print = True

# Push a chrono on the chrono stack
def start(desc = None):
	time_stack.append((time.time(), desc))
	if desc != None and time_print:
		print "[%s] Start" % desc

# Stop and pop a chrono from the stack
def end(_print = True):
	t, desc = time_stack.pop()
	t = time.time() - t
	if _print and time_print:
		if desc == None:
			print "Stop: %f" % t
		else:
			print "[%s] Stop: %f" % (desc, t)
	return t
