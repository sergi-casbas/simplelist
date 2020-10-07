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
import sys
import sqlite3
import json
import secrets
from lib import smtplib
from lib.debug import dprint

class SimpleList:
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

		# Read default configuration file.
		self.configs = self.read_configuration("./default.json")
		if 'config' in self.arguments:  # Overload with user defined configurations.
			for key,value  in self.read_configuration(self.arguments['config']).items():
				if isinstance(value, dict): #TODO Infinite recursive.
					for subkey, subvalue in value.items():
						self.configs[key][subkey] = subvalue
				else:
					self.configs[key] = value

		# Set verbosity if no argument is set and exists in config file.
		if 'verbose' not in self.arguments and 'verbose' in self.configs:
			self.debug_level = int(self.configs['verbose'])

		# Open database connection.
		self.connection = self.open_connection(self.configs['database'])

		# Configure mta parameters.
		self.mta = self.configs['mta']
		self.mta['domain'] = self.arguments['domain']

	def extract_command_and_maillist(self, arguments):
		""" Extract command and maillist name from arguments """
		command = self.arguments['local'].split("-", 1)[0]
		local = arguments['local']
		domain = arguments['domain']
		maillist = f"{local}@{domain}" # Default maillist

		if command in 'unsubscribe, subscribe, members':
			try:
				maillist = local.split("-", 1)[1]+f'@{domain}'
			except IndexError:
				command = 'error'
		elif command in 'grant':
			try:
				maillist = local.split("-", 1)[1]
			except IndexError:
				command = 'error'
		else:
			if command not in 'help':
				command = 'forward'

		# Store values to class level dictionary
		self.arguments['maillist'] = maillist
		self.arguments['command'] = command

		# Return both values
		return command, maillist

	def main(self, mailbody):
		""" Main proceure orchestrator """
		# Extract if exist the command and maillist from the local argument.
		command, maillist = self.extract_command_and_maillist(self.arguments)
		arguments = self.arguments

		# Read body and store on global arguments.
		self.arguments['body']  = mailbody.read()
		body = self.arguments['body']

		# Store other usefull arguments.
		domain = arguments['domain']
		mailfrom = f'no-reply@{domain}'
		sender = arguments['sender']

		# Bouncing protection with auto-reply #1
		if "Auto-Submitted:" in body and  "Auto-Submitted: no" not in body:
			self.dprint(4, "Auto-Submitted message, ignore it")
			return 0 # If is a auto-submited ignoring it.
		if "Auto-Generated:" in body and "Auto-Generated: no" not in body:
			self.dprint(4, "Auto-Generated message, ignore it")
			return 0 # If is a auto-submited ignoring it.

		# TODO Confusing code, needs refactor.
		# Execute required validations and operations.
		self.dprint(5, f"Executing {command} command")
		if command in 'help, error':
			self.send_template(mailfrom, sender, command)
		elif command == 'unsubscribe':
			if self.check_membership(maillist, sender):
				self.unsubscribe(maillist, sender)
			else:
				self.send_template(mailfrom, sender, "error")
		elif command == 'subscribe':
			self.subscribe_request_authorization(maillist, sender)
		elif command == 'grant':
			self.subscribe_accept_authorization(mailfrom, sender, maillist)
		elif command == 'members':
			if self.check_membership(maillist, sender):
				self.members(maillist, sender)
			else:
				self.send_template(mailfrom, sender, "error")
		else:
			if self.check_membership(maillist, sender):
				self.forward(maillist, sender, body)
			else:
				self.send_template(f'no-reply@{domain}', sender, "error")

		# Commit any pending operation in the database.
		self.connection.commit()

		# If everything is OK, return 0
		return 0

	def read_configuration(self, config_file):
		""" Read configuration JSON and returns as dictionary """
		# read JSON
		self.dprint(5, f"Reading configuration file from {config_file}")
		with open(config_file, 'r') as json_file:
			configurations = json.loads(json_file.read())
		return configurations

	def open_connection(self, database):
		""" Open database based on config and return an open cursor to it """
		connection = None
		if database['rdms'] == "sqlite":
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

	def subscribe(self, maillist, address):
		""" Add the requester to the maillist """
		self.execute(f"INSERT OR IGNORE INTO subscriptions VALUES ('{maillist}','{address}')")
		self.send_template(maillist, address, "subscribe")

	def subscribe_request_authorization(self, maillist, address):
		""" Request admin authorization to subscribe if required """
		if not self.check_private(maillist):
			self.subscribe(maillist, address)
		#TODO Subscripcion delegada desde cuenta de administrador.
		# elif Mirar que address sea admin de la llista.
		# extreure addres del subject.
		# self.subscribe(maillist, subject)
		else:
			self.dprint(5, "Requesting authorization")
			token = self.generate_token()

			# Remove previous requests if exists.
			sql = "DELETE FROM authorization WHERE " + \
				f"maillist='{maillist}' AND subscriptor='{address}'"
			self.execute(sql)

			# Generate new request.
			sql = "INSERT INTO authorization VALUES" + \
				f"('{token}', '{maillist}','{address}')"
			self.execute(sql)

			# Get admin mail address.
			# TODO Convert as function to reuse
			sql = f"SELECT administrator FROM private WHERE maillist='{maillist}';"
			row = self.cursor(sql).fetchone()
			administrator = row[0]

			# Send notification to the admin.
			self.send_template(maillist, f"{administrator}", "authorization", {'token': token})
		return 0

	def subscribe_accept_authorization(self, mailfrom, sender, token):
		""" Accept authorization token and subscribe user to the list. """
		# Get authorization from database.
		sql = f"SELECT maillist, subscriptor FROM authorization WHERE authorization='{token}';"
		row = self.cursor(sql).fetchone()
		if row is None:
			self.send_template(mailfrom, sender, "error")
		else:
			self.subscribe(row[0], row[1])

	def unsubscribe(self, maillist, address):
		""" Remove the requester from the maillist """
		self.execute("DELETE FROM subscriptions " + \
			f"WHERE maillist='{maillist}' AND subscriptor='{address}';")
		self.send_template(maillist, address, "unsubscribe")

	def members(self, maillist, address):
		""" Send the complete list of members of a maillist """
		self.dprint(6, 'Recovering list members')
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
		headers = f"Reply-To: {maillist}\n"
		headers = headers + f"List-ID: {maillist}\n"
		headers = headers + f"List-Help: help@{self.arguments['domain']}\n"
		headers = headers + f"List-Subscribe: <mailto: subscribe-{maillist}>\n"
		headers = headers + f"List-Unsubscribe: <mailto: unsubscribe-{maillist}>\n"

		for row in cursor.fetchall():
			self.send_mail(maillist, row[0], headers + body)

	def check_private(self, maillist):
		""" Check if a maillist is declared private in the database """
		sql = f"SELECT count(*)=1 FROM private WHERE maillist='{maillist}';"
		return self.cursor(sql).fetchone()[0]

	def check_membership(self, maillist, address):
		""" Check if a addres exists in a maillist. """
		self.dprint(6, 'Checking membership')
		sql = "SELECT count(*)=1 FROM subscriptions WHERE " + \
			f"maillist = '{maillist}' and subscriptor='{address}';"
		row = self.cursor(sql).fetchone()
		return row[0]

	def send_mail(self, mailfrom, address, body):
		""" Sends and email through the MTA """
		self.dprint(5, f"Sending email from:{mailfrom} to:{address}")
		self.dprint(6, f"MTA connection: {self.mta}")
		server = smtplib.SMTP(self.mta['host'], self.mta['port'])
		server.set_debuglevel(self.debug_level >= 7)
		server.sendmail(mailfrom, address, body)
		server.quit()

	def send_template(self, mailfrom, address, template, replacements={}):
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
			self.send_mail(mailfrom, address, template)

	def generate_token(self):
		""" Generate a random token """
		if 'unit-tests' in self.arguments:
			return "ffffffff"
		else:
			return secrets.token_hex(4)

	def dprint(self, level, debug_message): # TODO Improve as class.
		"""" Call external class dprint function """
		#import logging
		#logging.basicConfig(level=logging.DEBUG)
		#logging.debug(debug_message)
		dprint(self.debug_level, level, debug_message)

def run_normal():
	""" Execute it with normal behaviour """
	procesor = SimpleList(sys.argv)
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
	run_unit_test(vfrom, "grant-00000000", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "subscribe-private", domain, "./unit-test/empty.eml")
	run_unit_test(vfrom, "grant-ffffffff", domain, "./unit-test/empty.eml")

def run_unit_test(sender, local, domain, bodyfilepath):
	""" Run unitary test """
	argv = sys.argv + [f"--sender={sender}", f"--local={local}", f"--domain={domain}"]
	procesor = SimpleList(argv)
	procesor.main(open(bodyfilepath, "rt"))
	time.sleep(1)

if __name__ == '__main__':
	if '--unit-tests' in sys.argv:
		run_unit_tests()
	else:
		run_normal()
