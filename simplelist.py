#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  simplelist.py
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
""" Simple implementation mail lists with getmail and SMTP """
import os
import json
import time
import random

time_milliseconds = lambda: int(round(time.time() * 1000))
global debug_level

def dprint(level, debug_message): # TO-DO Improve as class.
	"""" Call external class dprint function """
	from debug import dprint
	dprint(debug_level, level, debug_message)

def main(sys_arguments, mailbody):
	""" Main proceure orchestrator """
	# Local variables.
	arguments = {}
	configs = {}
	cursor = None

	# Convert arguments into a indexed list.
	for argument in sys_arguments:
		splited = argument.split("=")
		if len(splited) == 2:
			arguments[splited[0][2:]] = splited[1]

	# Extract if exist the command from the local argument.
	arguments['command'] = arguments['local'].split("-", 1)[0]

	if arguments['command'] in 'unsubscribe, subscribe':
		arguments['maillist'] = arguments['local'].split("-", 1)[1]+'@'+arguments['domain']
	else:
		arguments['command'] = 'forward'
		arguments['maillist'] = arguments['local']+'@'+arguments['domain']

	# Read configuration file.
	configs = read_configuration("./default.json")

	# Store messages to local maildir directory if not disabled.
	if configs['storage']['disabled']:
		dprint(7, "Messages storing is disabled")
	else:
		store_message(configs['storage'], arguments, sys_arguments, mailbody.read())

	# Open database cursor.
	cursor = open_database_cursor(configs['database'])
	return 0

def read_configuration(config_file):
	""" Read configuration JSON and returns as dictionary """
	# read JSON
	dprint(7, f"Reading configuration file from {config_file}")
	with open(config_file, 'r') as JSON_file:
		configurations = json.loads(JSON_file.read())
	return configurations

def store_message(storage, arguments, sys_arguments, body):
	""" Store the message and arguments into the mailist directory using maildir """
	dirlist = f"{storage['directory']}/{arguments['maillist']}"
	messageid = time_milliseconds()+(random.random())

	args_file = f"{dirlist}/args/{messageid}.simplelist"
	body_file = f"{dirlist}/new/{messageid}.simplelist"

	dprint(7, f"Storing arguments on {args_file}")
	store_file_autocreate_parent(args_file, str(sys_arguments))

	dprint(7, f"Storing email body on {body_file}")
	store_file_autocreate_parent(body_file, body)

def store_file_autocreate_parent(filename, contents):
	""" Stores the contents into filename, autocreate parent if required s"""
	try:
		with open(filename, "w") as file_object:
			file_object.write(contents)
	except FileNotFoundError:
		folder_path = os.path.dirname(os.path.abspath(filename))
		dprint(6, f"Folder {folder_path} not found, creating it.")
		os.makedirs(folder_path)
		store_file_autocreate_parent(filename, contents)

def open_database_cursor(database):
	""" Open database based on config and return an open cursor to it """
	cursor = None
	if database['rdms'] == "sqlite":
		import sqlite3
		dprint(7, "Connection to database sqlite://" + database['path'])
		cursor = sqlite3.connect(database['path'])
	else:
		raise ValueError('Wrong RDMS engine selected', database['rdms'])
	return cursor

def unsubscribe(database, maillist, arguments):
	""" Remove the requester from the maillist """
####### Esborra'l de la base de dades.
####### notifica al remitent la baixa.
	return

def subscribe(database, maillist, body):
	""" Add the requester to the maillist """
####### Afegeix-lo a la base de dades.
####### notifica al remitent l'alta.
	return

def forward(database, maillist, body):
	""" Send reciveid mail to all users in the maillist """
####### busca tots els remitent a la base de dades.
####### Reenvia el correu a tots els destinataris.
	return

if __name__ == '__main__':
	import sys
	debug_level = 7 #TO-DO read from sys.argv.
	sys.exit(main(sys.argv, sys.stdin))
