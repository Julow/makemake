# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    source_finder.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 12:58:39 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/15 17:14:01 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import config

#
# Search source files in a dir
#  return a list of absolute path to the sources
#

def find(start_dir):
	sources = []
	for curr_dir, dirs, ls in os.walk(start_dir):
		if os.path.basename(curr_dir) in config.EXCLUDE_DIRS:
			del dirs[:]
		else:
			for file_name in ls:
				for ext in config.SOURCE_EXT:
					if file_name.endswith(ext):
						sources.append(os.path.join(curr_dir, file_name))
						break
	return sources
