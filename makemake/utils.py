# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/03 09:35:59 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/03 09:36:36 by jaguillo         ###   ########.fr        #
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
