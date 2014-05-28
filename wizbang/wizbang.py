#!/bin/python

import requests

# Properties:
# 	menu
#		returns the entire menu
# 	account_types
#		returns a list of all account types and settings
#
# Methods:
# 	order(customer, order, tender)
#		send the order object to the server and updates with the results
# 	get_account(id=id, number=number)
#		returns an Account object
# 	get_invoice(id=id, number=number, outletid=outletid, txtcode=txtcode)
#		returns invoice details
# 	get_print_messages(outlet=outletid)
#		returns a PrintMessages object

class WizBang(object):
	def __init__(self, server_url, server_port):
		self.server_url = server_url
		self.server_port = server_port

	@property
	def menu(self):
		return

	@property
	def account_types(self):
		return

	def order(self, customer=None, order=None, tender=None):
		return

	def get_account(self, id=None, number=None):
		return

	def get_invoice(self, id=None, number=None, outlet=None, txtcode=None):
		return

	def get_print_messages(self, outlet=None):
		return

class Account(object):
	def __init__(self):
		return

class PrintMessages(object):
	def __init__(self):
		return

class Customer(object):
	def __init__(self):
		return

class Order(object):
	def __init__(self):
		return

class Tender(object):
	def __init__(self):
		return