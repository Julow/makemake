# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/10/15 09:22:52 by jaguillo          #+#    #+#              #
#    Updated: 2015/10/15 09:25:59 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import module_searcher

try:
	modules = module_searcher.load()
	for m in modules:
		print str(m)
except str as e:
	print "Error: %s" % e
	exit(1)
