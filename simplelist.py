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

import json

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

#### PSEUDO PYTHON
##### Guarda el missatge original i els arguments a la carpeta del grup <llista-correu>/new.
##### Sí comença per "unsubscribe-*"
###### unsubscribe(llista-correu,remitent).
##### oSí comença per "subscribe-*"
###### subscribe(llista-correu,remitent).
##### oSi no s'ha complert cap de les anterior.
###### forward(llista-correu, missatge)
	return 0

def read_configuration(config_file):
	""" Read configuration JSON and returns as dictionary """
	# read JSON
	with open(config_file, 'r') as JSON_file:
		configurations = json.loads(JSON_file.read())
	return configurations

def store_message(storage, maillist, arguments, body):
	""" Store the message and arguments into the mailist directory using maildir """
###### Guarda el missatge original i els arguments a la carpeta del grup <llista-correu>/new.
	return

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
	sys.exit(main(sys.argv, sys.stdin))
