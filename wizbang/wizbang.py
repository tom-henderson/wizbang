#!/bin/python

import requests
from BeautifulSoup import BeautifulSoup

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

class WBMenu(object):
	def __init__(self):
		self.items = []
		self.item_groups = []
		self.modifiers = []
		self.modifier_groups = []

	class WBItem(object):
		def __init__(self, id, local_id, name, price_1, price_2, price_3, price_4, price_5, price_6, item_group_id, modifier_groups=[]):
			self.id = id
			self.local_id = local_id
			self.name = name
			self.price_1 = price_1
			self.price_2 = price_2
			self.price_3 = price_3
			self.price_4 = price_4
			self.price_5 = price_5
			self.price_6 = price_6
			self.modifier_groups = modifier_groups

		def __repr__(self):
			return "{}: {} (${})".format(self.id, self.name, self.price_1)

	class WBItemGroup(object):
		def __init__(self, id, local_id, name, forb):
			self.id = id
			self.local_id = local_id
			self.name = name
			self.forb = forb
			self.items = []

		def __repr__(self):
			return "{}: {} ({})".format(self.id, self.name, len(self.items))

	class WBModifier(object):
		def __init__(self, id, local_id, name, forb, price):
			self.id = id
			self.local_id = local_id
			self.name = name
			self.forb = forb
			self.price = price

		def __repr__(self):
			return "{}: {}".format(self.id, self.name)

	class WBModifierGroup(object):
		def __init__(self, id, local_id, name, forb, force, multi, prompt, proceed, items, modifiers):
			self.id = id
			self.local_id = local_id
			self.name = name
			self.forb = forb
			self.force = force
			self.multi = multi
			self.prompt = prompt
			self.proceed = proceed
			self.items = items
			self.modifiers = modifiers

		def __repr__(self):
			return "{}: {} ({} items, {} mods)".format(self.id, self.name, len(self.items), len(self.modifiers))

	def item(self, id):
		for item in self.items:
			if item.id == str(id):
				return item
		return None

	def item_group(self, id=None):
		for item_group in self.item_groups:
			if item_group.id == str(id):
				return item_group
		return None

	def modifier(self, id):
		for modifier in self.modifiers:
			if modifier.id == str(id):
				return modifier
		return None
	
	def modifier_group(self, id):
		for modifier_group in self.modifier_groups:
			if modifier_group.id == str(id):
				return modifier_group
		return None

	def add_item(self, id, local_id, name, price_1, price_2, price_3, price_4, price_5, price_6, item_group_id):
		self.items.append(self.WBItem(id, local_id, name, price_1, price_2, price_3, price_4, price_5, price_6, item_group_id))

	def add_item_group(self, id, local_id, name, forb):
		self.item_groups.append(self.WBItemGroup(id, local_id, name, forb))

	def add_modifier(self, id, local_id, name, forb, price):
		self.modifiers.append(self.WBModifier(id, local_id, name, forb, price))

	def add_modifier_group(self, id, local_id, name, forb, force, multi, prompt, proceed, item_ids, modifier_ids):
		items = [self.item(item_id) for item_id in item_ids]
		modifiers = [self.modifier(modifier_id) for modifier_id in modifier_ids]
		self.modifier_groups.append(self.WBModifierGroup(id, local_id, name, forb, force, multi, prompt, proceed, items, modifiers))

class WizBang(object):
	def __init__(self, server_url, server_port):
		self.server_url = server_url
		self.server_port = server_port
		self.menu = self.get_menu()

	def get_id(self, item):
		return [attr for attr in item.attrs if 'id' in attr[0]][0][1]

	def get_menu(self):
		data = requests.get("http://{}:{}/menu.xml".format(self.server_url, self.server_port))
		soup = BeautifulSoup(data.text)
		menu = WBMenu()

		for item_group in soup.itemgroups.findAll("itemgroup"):
			item_group_id = self.get_id(item_group)
			local_id = item_group.find("localitemgroupid").text
			name = item_group.find("name").text
			forb = item_group.find("forb").text

			menu.add_item_group(item_group_id, local_id, name, forb)

		for item in soup.items.findAll("item"):
			item_id = self.get_id(item)
			local_id = item.find("localitemid").text
			name = item.find("name").text
			price_1 = item.find("price1").text
			price_2 = item.find("price2").text
			price_3 = item.find("price3").text
			price_4 = item.find("price4").text
			price_5 = item.find("price5").text
			price_6 = item.find("price6").text
			item_group_id = self.get_id(item.find("itemgroup"))

			menu.add_item(item_id, local_id, name, price_1, price_2, price_3, price_4, price_5, price_6, item_group_id)
			menu.item_group(item_group_id).items.append(menu.item(item_id))

		for modifier in soup.modifiers.findAll("modifier"):
			mod_id = self.get_id(modifier)
			local_id = modifier.find("localmodifierid").text
			name = modifier.find("name").text
			forb = modifier.find("localmodifierid").text
			price = modifier.find("price").text

			menu.add_modifier(mod_id, local_id, name, forb, price)

		for modifier_group in soup.modgroups.findAll("modgroup"):
			modifier_group_id = self.get_id(modifier_group)
			local_id = modifier_group.find("localmodgroupid").text
			name = modifier_group.find("name").text
			forb = modifier_group.find("forb").text
			force = modifier_group.find("force").text
			multi = modifier_group.find("multi").text
			prompt = modifier_group.find("prompt").text
			proceed = modifier_group.find("proceed").text
			if modifier_group.items:
				item_ids = [self.get_id(item) for item in modifier_group.items.findAll("item")]
			if modifier_group.modifiers:
				modifier_ids = [self.get_id(modifier) for modifier in modifier_group.modifiers.findAll("modifier")]

			menu.add_modifier_group(modifier_group_id, local_id, name, forb, force, multi, prompt, proceed, item_ids, modifier_ids)

		return menu


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