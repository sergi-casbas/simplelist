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
from datetime import datetime

# Colours and tags for printing debug messages using ANSI escapes """
debug_levels = [["EMERG", "\033[4m\033[1m\033[91m"], \
				["ALERT", "\033[1m\033[91m"], \
				["CRITC", "\033[91m"], \
				["ERROR", "\033[31m"], \
				["WARNG", "\033[33m"], \
				["NOTIC", "\033[32m"], \
				[" INFO", "\033[97m"], \
				["DEBUG", "\033[37m"]]

def dprint(debug_level, level, debug_message):
	""" Print debug informaiton in different debug levels """
	tag, colour = debug_levels[level]
	dateTimeObj = datetime.now()
	timestampStr = dateTimeObj.strftime("[%Y-%m-%d %H:%M:%S]")
	if level <= debug_level:
		print(f"{timestampStr} {colour}[{tag}]: {debug_message}\033[0m")

def demo_mode():
	""" Show a sample of each type of debug message """
	for level in range(0, 8):
		dprint(8, level, f"demo mode - this is level: {level}")

if __name__ == '__main__':
	# Call demo mode if script is called stand-alone
	demo_mode()
