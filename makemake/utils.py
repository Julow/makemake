# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/03 09:35:59 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/11 01:47:04 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import webbrowser
import subprocess
import sys

def open_browser(url):
	if sys.platform == 'darwin':
		subprocess.Popen(['open', url])
	else:
		webbrowser.open(url, 0, True)

def warn(msg):
	print "\033[33mWarning:\033[0m %s" % msg

def error(msg):
	print "\033[31mError:\033[0m %s" % msg
