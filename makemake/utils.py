# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/03 09:35:59 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/12 17:30:50 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import webbrowser
import subprocess
import sys
import config
import re

VARIABLE_REG = re.compile(config.VARIABLE_REG)

# Open url in a browser
def open_browser(url):
	if sys.platform == 'darwin':
		subprocess.Popen(['open', url])
	else:
		webbrowser.open(url, 0, True)

# Substitute ?variables? in text
def substitute_vars(text, v):
	return VARIABLE_REG.sub(lambda m: v[m.group(1)] if m.group(1) in v else m.group(0), text)

def warn(msg):
	print "\033[33mWarning:\033[0m %s" % msg

def error(msg):
	print "\033[31mError:\033[0m %s" % msg
