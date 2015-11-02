# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    setup.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/11/01 10:10:17 by jaguillo          #+#    #+#              #
#    Updated: 2015/11/02 22:47:25 by juloo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import makemake

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

def cat_readme():
	with open('README.md') as f:
		return f.read()

setup(
	name='makemake',
	version=1.0,
	description="Makefile and dependency generator",
	long_description=cat_readme(),
	url='https://github.com/Julow/makemake',
	author=makemake.__author__,
	packages=['makemake'],
	entry_points={'console_scripts': ['makemake2 = makemake.__main__:main']},
	keywords=['makemake', 'makemake2'],
	data_files=[('makemake/res', ['makemake/res/module_print.html'])],
)
