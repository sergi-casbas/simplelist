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
import smtplib

global debug_level
debug_level = 0
time_milliseconds = lambda: int(round(time.time() * 1000))

def dprint(level, debug_message): # TO-DO Improve as class.
	"""" Call external class dprint function """
	from debug import dprint
	dprint(debug_level, level, debug_message)

def main(sys_arguments, mailbody):
	""" Main proceure orchestrator """
	# Global variables
	global debug_level
    
    # Local variables.
	arguments = {}
	configs = {}
	connection = None

	# Convert arguments into a indexed list.
	for argument in sys_arguments:
		splited = argument.split("=")
		if len(splited) == 2:
			arguments[splited[0][2:]] = splited[1]

	# Establish debug level by argument or by default.
	if 'verbose' in arguments:
		debug_level = int(arguments['verbose'])
	else:
		debug_level = 0

	# Extract if exist the command from the local argument.
	arguments['command'] = arguments['local'].split("-", 1)[0]
	if arguments['command'] in 'help, unsubscribe, subscribe':
		arguments['maillist'] = arguments['local'].split("-", 1)[1]+'@'+arguments['domain']
	else:
		arguments['command'] = 'forward'
		arguments['maillist'] = arguments['local']+'@'+arguments['domain']

	# Read configuration file.
	configs = read_configuration(f"{arguments['config']}")

	# Store messages to local maildir directory if not disabled.
	if configs['storage']['disabled']:
		dprint(6, "Messages storing is disabled")
	else:
		store_message(configs['storage'], arguments, sys_arguments, mailbody.read())

	# Open database connection.
	connection = open_connection(configs['database'])
	mta = configs['mta']

	# Execute required operation.
	dprint(5, f"Executing {arguments['command']} command")
	if arguments['command'] == 'help':
		send_help(mta, arguments['maillist'], arguments['sender'])
	elif arguments['command'] == 'unsubscribe':
		unsubscribe(connection.cursor(), mta, arguments['maillist'], arguments['sender'])
	elif arguments['command'] == 'subscribe':
		subscribe(connection.cursor(), mta, arguments['maillist'], arguments['sender'])
	else:
		forward(connection.cursor(), mta, arguments['maillist'], mailbody.read())

	# Commit any pending operation in the database.
	connection.commit()

	# If everything is OK, return 0
	return 0

def read_configuration(config_file):
	""" Read configuration JSON and returns as dictionary """
	# read JSON
	dprint(5, f"Reading configuration file from {config_file}")
	with open(config_file, 'r') as JSON_file:
		configurations = json.loads(JSON_file.read())
	return configurations

def store_message(storage, arguments, sys_arguments, body):
	""" Store the message and arguments into the mailist directory using maildir """
	dirlist = f"{storage['directory']}/{arguments['maillist']}"
	messageid = time_milliseconds()+(random.random())

	args_file = f"{dirlist}/args/{messageid}.simplelist"
	body_file = f"{dirlist}/new/{messageid}.simplelist"

	dprint(6, f"Storing arguments on {args_file}")
	store_file_autocreate_parent(args_file, str(sys_arguments))

	dprint(6, f"Storing email body on {body_file}")
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

def open_connection(database):
	""" Open database based on config and return an open cursor to it """
	connection = None
	if database['rdms'] == "sqlite":
		import sqlite3
		dprint(6, "Connection to database sqlite://" + database['path'])
		connection = sqlite3.connect(database['path'])
	else:
		raise ValueError('Wrong RDMS engine selected', database['rdms'])
	return connection

def send_help(mta, maillist, address): #7
	""" Send help template information to the requester """
	send_template(mta, maillist, address, "help")

def unsubscribe(cursor, mta, maillist, address):
	""" Remove the requester from the maillist """
	sql = f"DELETE FROM subscriptions WHERE maillist='{maillist}' AND subscriptor='{address}';"
	dprint(6, f'Executing SQL: {sql}')
	cursor.execute(sql)
	send_template(mta, maillist, address, "unsubscribe")
####### notifica al remitent la baixa.

def subscribe(cursor, mta, maillist, address):
	""" Add the requester to the maillist """
	sql = f"INSERT OR IGNORE INTO subscriptions VALUES ('{maillist}','{address}')"
	dprint(6, f'Executing SQL: {sql}')
	cursor.execute(sql)
	send_template(mta, maillist, address, "subscribe")
####### notifica al remitent l'alta.

def forward(cursor, mta, maillist, body):
	""" Send reciveid mail to all users in the maillist """
	sql = f"SELECT subscriptor FROM subscriptions WHERE maillist = '{maillist}';"
	dprint(6, f'Executing SQL: {sql}')
	cursor.execute(sql)
	EOC = False
	while not EOC:
		address = cursor.fetchone()
		if address is None:
			EOC = True
		else:
			send_mail(mta, maillist, address[0], body)

def send_mail(mta, sender, address, body):
	""" Sends and email through the MTA """
	dprint(5, f"Sending email from:{sender} to:{address}")
	dprint(6, f"MTA connection: {mta}")
	server = smtplib.SMTP(mta['host'], mta['port'])
	server.set_debuglevel(debug_level >= 7)
	server.sendmail(sender, address, body)
	server.quit()

def send_template(mta, sender, address, template):
	""" Sends a template email to comunicate commands information """
	template_file = mta['templates'] + f"/{template}.eml"
	dprint(6, f"Opening template {template_file}")
	with open(template_file, "r") as file_object:
		template = file_object.read()
		template = template.replace("{maillist}", sender)
		send_mail(mta, sender, address, template)

if __name__ == '__main__':
	import sys
	import traceback

	try:
		sys.exit(main(sys.argv, sys.stdin))
	except Exception as error:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		trace = traceback.extract_tb(exc_traceback, limit=-1)
		dprint(0, trace.format())
		sys.exit(1)
