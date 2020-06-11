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
def main(arguments, mailbody):
	with open("test/args.txt", "w") as myfile:
		myfile.write(str(arguments)+"\n")

	with open("test/body.txt", "w") as myfile:
		for line in mailbody.read():
			myfile.write(line)

#### PSEUDO PYTHON

##### Converteix arguments en llista indexada.
##### Llegeix arxiu de configuració
##### Guarda el missatge original i els arguments a la carpeta del grup <llista-correu>/new.
##### Sí comença per "unsubscribe-*"
###### unsubscribe(llista-correu,remitent).
##### oSí comença per "subscribe-*"
###### subscribe(llista-correu,remitent).
##### oSi no s'ha complert cap de les anterior.
###### forward(llista-correu, missatge)


def read_configuration(config_file):
###### on es guardaran els missatges.
###### parametres de connexio a la sqlite.
###### parametres de connexio smtp.
	return

def store_message(storage, maillist, arguments, body):
###### Guarda el missatge original i els arguments a la carpeta del grup <llista-correu>/new.
	return

def unsubscribe(database, maillist, arguments):
####### Esborra'l de la base de dades.
####### notifica al remitent la baixa.
	return

def subscribe(database, maillist, body):
####### Afegeix-lo a la base de dades.
####### notifica al remitent l'alta.
	return

def forward(database, maillist, body):
####### busca tots els remitent a la base de dades.
####### Reenvia el correu a tots els destinataris.
	return

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv, sys.stdin))
