# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    source_finder.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 12:58:39 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/31 16:55:44 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import config

#
# Search source files in a dir
#  return a list of tuple (absolute path, ext data)
#

def find(start_dir):
	sources = []
	for curr_dir, dirs, ls in os.walk(start_dir):
		if os.path.basename(curr_dir) in config.EXCLUDE_DIRS:
			del dirs[:]
		else:
			for file_name in ls:
				for ext in config.EXTENSIONS:
					if not ext["is_source"]:
						continue
					if file_name.endswith(ext["ext"]):
						sources.append((os.path.join(curr_dir, file_name), ext))
						break
	return sources