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
import smtplib

class simplelist:
	""" Main class """
	def __init__(self):
		self.debug_level = 0

	def dprint(self, level, debug_message): # TO-DO Improve as class.
		"""" Call external class dprint function """
		#import logging
		#logging.basicConfig(level=logging.DEBUG)
		#logging.debug(debug_message)
		from debug import dprint
		dprint(self.debug_level, level, debug_message)

	def main(self, sys_arguments, mailbody):
		""" Main proceure orchestrator """
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
			self.debug_level = int(arguments['verbose'])
		else:
			self.debug_level = 0

		# Extract if exist the command from the local argument.
		arguments['command'] = arguments['local'].split("-", 1)[0]
		if arguments['command'] in 'help':
			arguments['maillist'] = arguments['local']+'@'+arguments['domain']
		elif arguments['command'] in 'unsubscribe, subscribe':
			try:
				arguments['maillist'] = arguments['local'].split("-", 1)[1]+'@'+arguments['domain']
			except IndexError:
				arguments['command'] = 'error'
				arguments['maillist'] = arguments['local']+'@'+arguments['domain']
		else:
			arguments['command'] = 'forward'
			arguments['maillist'] = arguments['local']+'@'+arguments['domain']
		arguments['body'] = mailbody.read()

		# Read configuration file.
		if 'config' in arguments:
			configs = self.read_configuration(arguments['config'])
		else:
			configs = self.read_configuration("./default.json")

		# Set verbosity if no argument is set and exists in config file.
		if 'verbose' not in arguments and 'verbose' in configs:
			self.debug_level = int(configs['verbose'])

		# TO-DO white and blacklists. #2 i #3

		# Bouncing protection with auto-reply #1
		if "Auto-Submitted:" in arguments['body'] and  "Auto-Submitted: no" not in arguments['body']:
			self.dprint(4, "Auto-Submitted message, ignore it")
			return 0 # If is a auto-submited ignoring it.
		if "Auto-Generated:" in arguments['body'] and "Auto-Generated: no" not in arguments['body']:
			self.dprint(4, "Auto-Generated message, ignore it")
			return 0 # If is a auto-submited ignoring it.

		# Open database connection.
		connection = self.open_connection(configs['database'])
		mta = configs['mta']
		mta['domain'] = arguments['domain']

		# Execute required operation.
		self.dprint(5, f"Executing {arguments['command']} command")
		if arguments['command'] in 'help, error':
			self.send_template(mta, 'no-reply@'+arguments['domain'], arguments['sender'], arguments['command'])
		elif arguments['command'] == 'unsubscribe':
			self.unsubscribe(connection.cursor(), mta, arguments['maillist'], arguments['sender'])
		elif arguments['command'] == 'subscribe':
			# Limit to existing lists #6
			self.subscribe(connection.cursor(), mta, arguments['maillist'], arguments['sender'])
		else:
			# Require user subscription to forward #4
			self.forward(connection.cursor(), mta, arguments['maillist'], arguments['sender'], arguments['body'])

		# Commit any pending operation in the database.
		connection.commit()

		# If everything is OK, return 0
		return 0

	def read_configuration(self, config_file):
		""" Read configuration JSON and returns as dictionary """
		# read JSON
		self.dprint(5, f"Reading configuration file from {config_file}")
		with open(config_file, 'r') as JSON_file:
			configurations = json.loads(JSON_file.read())
		return configurations

	def open_connection(self, database):
		""" Open database based on config and return an open cursor to it """
		connection = None
		if database['rdms'] == "sqlite":
			import sqlite3
			self.dprint(6, "Connection to database sqlite://" + database['path'])
			connection = sqlite3.connect(database['path'])
		else:
			raise ValueError('Wrong RDMS engine selected', database['rdms'])
		return connection

	def send_help(self, mta, maillist, address): #7
		""" Send help template information to the requester """
		self.send_template(mta, maillist, address, "help")

	def send_error(self, mta, maillist, address):
		""" Send a failure error to the sender """
		self.send_template(mta, maillist, address, "error")

	def unsubscribe(self, cursor, mta, maillist, address):
		""" Remove the requester from the maillist """
		sql = f"DELETE FROM subscriptions WHERE maillist='{maillist}' AND subscriptor='{address}';"
		self.dprint(6, f'Executing SQL: {sql}')
		cursor.execute(sql)
		self.send_template(mta, maillist, address, "unsubscribe")

	def subscribe(self, cursor, mta, maillist, address):
		""" Add the requester to the maillist """
		sql = f"INSERT OR IGNORE INTO subscriptions VALUES ('{maillist}','{address}')"
		self.dprint(6, f'Executing SQL: {sql}')
		cursor.execute(sql)
		self.send_template(mta, maillist, address, "subscribe")

	def forward(self, cursor, mta, maillist, address, body):
		""" Send reciveid mail to all users in the maillist """
		sql = f"SELECT subscriptor FROM subscriptions WHERE maillist = '{maillist}' AND subscriptor <> '{address}';"
		self.dprint(6, f'Executing SQL: {sql}')
		cursor.execute(sql)
		EOC = False
		body = f"Reply-To: {maillist}\n" + body
		while not EOC:
			address = cursor.fetchone()
			if address is None:
				EOC = True
			else:
				self.send_mail(mta, maillist, address[0], body)

	def send_mail(self, mta, sender, address, body):
		""" Sends and email through the MTA """
		self.dprint(5, f"Sending email from:{sender} to:{address}")
		self.dprint(6, f"MTA connection: {mta}")
		server = smtplib.SMTP(mta['host'], mta['port'])
		server.set_debuglevel(self.debug_level >= 7)
		server.sendmail(sender, address, body)
		server.quit()

	def send_template(self, mta, sender, address, template):
		""" Sends a template email to comunicate commands information """
		template_file = mta['templates'] + f"/{template}.eml"
		self.dprint(6, f"Opening template {template_file}")
		with open(template_file, "r") as file_object:
			template = file_object.read()
			template = template.replace("{maillist}", sender)
			template = template.replace("{domain}", mta['domain'])
			template = template + "\n\n" + ('-'*80)
			template = template + "\nMake your mail lists simply with Simplelist\n"
			self.send_mail(mta, sender, address, template)


if __name__ == '__main__':
	import sys
	import traceback

	procesor = simplelist()

	sys.exit(procesor.main(sys.argv, sys.stdin))

	#try:
	#	sys.exit(procesor.main(sys.argv, sys.stdin))
	#except Exception as error:
	#	exc_type, exc_value, exc_traceback = sys.exc_info()
	#	trace = traceback.extract_tb(exc_traceback, limit=-1)
	#	self.dprint(0, f'{type(exc_value)} {trace.format()[0]}')
	#	sys.exit(1)
