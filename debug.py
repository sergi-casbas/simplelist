#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  debug.py
#
#  Copyright 2020 Sergi Casbas <sergi@casbas.cat>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
""" Class to handle and print debug messages """

class bcolors:
	""" Colours for printing debug messages using ANSI escapes """
	HEADER = '\033[95m'
	OKPURPLE = '\033[35m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def dprint(debug_level, level, debug_message):
	""" Print debug informaiton in different debug levels """
	colour = bcolors.FAIL
	if level == 7:
		colour = bcolors.OKGREEN
	elif level == 6:
		colour = bcolors.WARNING
	if level <= debug_level:
		print(f"{colour}[INFO]:{debug_message}{bcolors.ENDC}")
