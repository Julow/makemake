# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/03 09:35:59 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/05 19:24:50 by jaguillo         ###   ########.fr        #
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
