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
from lib import smtplib
from lib.debug import dprint

class simplelist:
	""" Main class """
	def __init__(self, sys_arguments):
		# class variables.
		self.arguments = {}
		self.configs = {}
		self.connection = None

		# Convert arguments into a indexed list.
		for argument in sys_arguments[1:]:
			splited = argument.split("=")
			if len(splited) == 1:
				self.arguments[splited[0][2:]] = True
			elif len(splited) == 2:
				self.arguments[splited[0][2:]] = splited[1]

		# Establish debug level by argument or by default (need here to verbose config read)
		if 'verbose' in self.arguments:
			self.debug_level = int(self.arguments['verbose'])
		else:
			self.debug_level = 0

		# Read configuration file.
		if 'config' in self.arguments:
			self.configs = self.read_configuration(self.arguments['config'])
		else:
			self.configs = self.read_configuration("./default.json")

		# Set verbosity if no argument is set and exists in config file.
		if 'verbose' not in self.arguments and 'verbose' in self.configs:
			self.debug_level = int(self.configs['verbose'])

		# Open database connection.
		self.connection = self.open_connection(self.configs['database'])

		# Configure mta parameters.
		self.mta = self.configs['mta']
		self.mta['domain'] = self.arguments['domain']

	def dprint(self, level, debug_message): # TODO Improve as class.
		"""" Call external class dprint function """
		#import logging
		#logging.basicConfig(level=logging.DEBUG)
		#logging.debug(debug_message)
		dprint(self.debug_level, level, debug_message)

	def main(self, mailbody):
		""" Main proceure orchestrator """
		# Extract if exist the command from the local argument.
		arguments = self.arguments
		arguments['command'] = arguments['local'].split("-", 1)[0]
		if arguments['command'] in 'help':
			arguments['maillist'] = arguments['local']+'@'+arguments['domain']
		elif arguments['command'] in 'unsubscribe, subscribe, members':
			try:
				arguments['maillist'] = arguments['local'].split("-", 1)[1]+'@'+arguments['domain']
			except IndexError:
				arguments['command'] = 'error'
				arguments['maillist'] = arguments['local']+'@'+arguments['domain']
		else:
			arguments['command'] = 'forward'
			arguments['maillist'] = arguments['local']+'@'+arguments['domain']
		arguments['body'] = mailbody.read()

		# TODO white and blacklists. #2 i #3

		# Bouncing protection with auto-reply #1
		if "Auto-Submitted:" in arguments['body'] and  "Auto-Submitted: no" not in arguments['body']:
			self.dprint(4, "Auto-Submitted message, ignore it")
			return 0 # If is a auto-submited ignoring it.
		if "Auto-Generated:" in arguments['body'] and "Auto-Generated: no" not in arguments['body']:
			self.dprint(4, "Auto-Generated message, ignore it")
			return 0 # If is a auto-submited ignoring it.

		# TODO Confusing code, needs refactor.
		# Execute required validations and operations.
		self.dprint(5, f"Executing {arguments['command']} command")
		if arguments['command'] in 'help, error':
			self.send_template('no-reply@'+arguments['domain'], arguments['sender'], arguments['command'])
		elif arguments['command'] == 'unsubscribe':
			if self.check_membership(arguments['maillist'], arguments['sender']):
				self.unsubscribe(arguments['maillist'], arguments['sender'])
			else:
				self.send_template('no-reply@'+arguments['domain'], arguments['sender'], "error")
		elif arguments['command'] == 'subscribe':
			self.subscribe_request_authorization(arguments['maillist'], arguments['sender'])
		elif arguments['command'] == 'members':
			if self.check_membership(arguments['maillist'], arguments['sender']):
				self.members(arguments['maillist'], arguments['sender'])
			else:
				self.send_template('no-reply@'+arguments['domain'], arguments['sender'], "error")
		else:
			if self.check_membership(arguments['maillist'], arguments['sender']):
				self.forward(arguments['maillist'], arguments['sender'], arguments['body'])
			else:
				self.send_template('no-reply@'+arguments['domain'], arguments['sender'], "error")

		# Commit any pending operation in the database.
		self.connection.commit()

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

	def execute(self, sql):
		""" Execute SQL in the database, no response expected """
		self.dprint(6, f'Executing SQL: {sql}')
		self.connection.cursor().execute(sql)

	def cursor(self, sql):
		""" Open a query on the database, return a cursor to the results """
		self.dprint(6, f'Open query SQL: {sql}')
		cursor = self.connection.cursor()
		cursor.execute(sql)
		return cursor
	def send_help(self, maillist, address): #7
		""" Send help template information to the requester """
		self.send_template(maillist, address, "help")

	def send_error(self, maillist, address):
		""" Send a failure error to the sender """
		self.send_template(maillist, address, "error")


	def subscribe_request_authorization(self, maillist, address):
		""" Request admin authorization to subscribe (if required) """
		self.subscribe(maillist, address)
		return 0

	def subscribe(self, maillist, address):
		""" Add the requester to the maillist """
		self.execute(f"INSERT OR IGNORE INTO subscriptions VALUES ('{maillist}','{address}')")
		self.send_template(maillist, address, "subscribe")


		row = self.cursor(sql).fetchone()
		return row[0]
	def unsubscribe(self, maillist, address):
		""" Remove the requester from the maillist """
		self.execute(f"DELETE FROM subscriptions " + \
			"WHERE maillist='{maillist}' AND subscriptor='{address}';")
		self.send_template(maillist, address, "unsubscribe")

	def members(self, maillist, address):
		""" Send the complete list of members of a maillist """
		self.dprint(6, f'Recovering list members')
		sql = f"SELECT subscriptor FROM subscriptions WHERE maillist = '{maillist}' ORDER BY subscriptor;"
		subscriptors = []
		for row in self.cursor(sql).fetchall():
			subscriptors.append(row[0])
		self.send_template(maillist, address, "members", {'members': '\n'.join(subscriptors)})

	def forward(self, maillist, address, body):
		""" Send reciveid mail to all users in the maillist """
		sql = f"SELECT subscriptor FROM subscriptions \
			WHERE maillist = '{maillist}' AND subscriptor <> '{address}';"
		self.dprint(6, f'Executing SQL: {sql}')
		cursor = self.connection.cursor()
		cursor.execute(sql)

		body = f"Reply-To: {maillist}\n" + body
		for row in cursor.fetchall():
			self.send_mail(maillist, row[0], body)

	def check_membership(self, maillist, address):
		""" Check if a addres exists in a maillist. """
		self.dprint(6, f'Checking membership')
		sql = "SELECT count(*)=1 FROM subscriptions WHERE " + \
			f"maillist = '{maillist}' and subscriptor='{address}';"
		row = self.cursor(sql).fetchone()
		return row[0]

	def send_mail(self, sender, address, body):
		""" Sends and email through the MTA """
		self.dprint(5, f"Sending email from:{sender} to:{address}")
		self.dprint(6, f"MTA connection: {self.mta}")
		server = smtplib.SMTP(self.mta['host'], self.mta['port'])
		server.set_debuglevel(self.debug_level >= 7)
		server.sendmail(sender, address, body)
		server.quit()

	def send_template(self, sender, address, template, replacements={}):
		""" Sends a template email to comunicate commands information """
		template_file = self.mta['templates'] + f"/{template}.eml"
		self.dprint(6, f"Opening template {template_file}")
		with open(template_file, "r") as file_object:
			template = file_object.read()
			replacements = {**replacements, **self.mta}
			replacements = {**replacements, **self.arguments}
			for key, value  in replacements.items():
				template = template.replace("{"+key+"}", str(value))
			template = template + "\n\n" + ('-'*80)
			template = template + "\nMake your mail lists simply with Simplelist\n"
			self.send_mail(sender, address, template)


def run_normal():
	""" Execute it with normal behaviour """
	procesor = simplelist(sys.argv)
	sys.exit(procesor.main(sys.stdin))

def run_unit_tests():
	# Dummy smtp server: python -m smtpd -c DebuggingServer -n localhost:2525
	""" Execute unit tests included in this code. Usefull to debug """
	vfrom = "me@dummy.domain"
	domain = "lists.dummy.domain"
	run_unit_test(vfrom, "subscribe", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "help", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "help-me", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "subscribe-unit-test", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "unsubscribe-unit-test", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "subscribe-unit-test", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "unit-test", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "unit-test", domain, "./unit-test/body-auto-generated-no.eml")
	run_unit_test(vfrom, "unit-test", domain, "./unit-test/body-auto-generated.eml")
	run_unit_test(vfrom, "unit-test", domain, "./unit-test/body-auto-submitted.eml")
	run_unit_test("alter.ego@dummy.domain", "subscribe-unit-test", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "members-unit-test", domain, "./unit-test/empty.eml")
	run_unit_test("inexistent@dummy.domain", "members-unit-test", domain, "./unit-test/empty.eml")

def run_unit_test(sender, local, domain, bodyfilepath):
	""" Run unitary test """
	argv = sys.argv + [f"--sender={sender}", f"--local={local}", f"--domain={domain}"]
	procesor = simplelist(argv)
	procesor.main(open(bodyfilepath, "rt"))
	time.sleep(0.2)

if __name__ == '__main__':
	import sys
	import time
	if '--unit-tests' in sys.argv:
		run_unit_tests()
	else:
		run_normal()
