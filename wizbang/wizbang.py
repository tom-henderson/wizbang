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

class Menu(object):
	def __init__(self):
		self.items = []
		self.item_groups = []
		self.modifiers = []
		self.modifier_groups = []

	class Item(object):
		def __init__(self, id, local_id, name, price_1, price_2, price_3, price_4, price_5, price_6, item_group_id):
			self.id = id
			self.local_id = local_id
			self.name = name
			self.price_1 = price_1
			self.price_2 = price_2
			self.price_3 = price_3
			self.price_4 = price_4
			self.price_5 = price_5
			self.price_6 = price_6
			self.modifier_groups = []

		def __repr__(self):
			return "{}: {} (${})".format(self.id, self.name, self.price_1)

	class ItemGroup(object):
		def __init__(self, id, local_id, name, forb):
			self.id = id
			self.local_id = local_id
			self.name = name
			self.forb = forb
			self.items = []

		def __repr__(self):
			return "{}: {} ({})".format(self.id, self.name, len(self.items))

	class Modifier(object):
		def __init__(self, id, local_id, name, forb, price):
			self.id = id
			self.local_id = local_id
			self.name = name
			self.forb = forb
			self.price = price

		def __repr__(self):
			return "{}: {}".format(self.id, self.name)

	class ModifierGroup(object):
		def __init__(self, id, local_id, name, forb, force, multi, prompt, proceed, modifiers):
			self.id = id
			self.local_id = local_id
			self.name = name
			self.forb = forb
			self.force = force
			self.multi = multi
			self.prompt = prompt
			self.proceed = proceed
			self.modifiers = modifiers

		def __repr__(self):
			return "{}: {} ({})".format(self.id, self.name, len(self.modifiers))

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
		self.items.append(self.Item(id, local_id, name, price_1, price_2, price_3, price_4, price_5, price_6, item_group_id))

	def add_item_group(self, id, local_id, name, forb):
		self.item_groups.append(self.ItemGroup(id, local_id, name, forb))

	def add_modifier(self, id, local_id, name, forb, price):
		self.modifiers.append(self.Modifier(id, local_id, name, forb, price))

	def add_modifier_group(self, id, local_id, name, forb, force, multi, prompt, proceed, item_ids, modifier_ids):
		modifiers = [self.modifier(modifier_id) for modifier_id in modifier_ids]
		self.modifier_groups.append(self.ModifierGroup(id, local_id, name, forb, force, multi, prompt, proceed, modifiers))
		
		for item in [self.item(item_id) for item_id in item_ids]:
			if self.modifier_group(id) not in item.modifier_groups:
				item.modifier_groups.append(self.modifier_group(id))

	def print_menu_tree(self, mod_groups=False, modifiers=False):
		for ig in self.item_groups:
			print "+ {}".format(ig.name)
			for i in ig.items:
				print "|- {}".format(i.name)
				if i.modifier_groups and mod_groups:
					for mg in i.modifier_groups:
						print "| |- {}".format(mg.name)
						if mg.modifiers and mod_groups and modifiers:
							for m in mg.modifiers:
								print "| | |- {}".format(m.name)
							print "| |"
					print "|"
			print

class Order(object):
	def __init__(self):
		self.items = []

	def add_item(self, item, quantity):
		self.items.append({
					"item": item,
					"quantity": quantity,
				})

class Customer(object):
	def __init__(self):
		self.id = ""
		self.name = ""
		self.surname = ""
		self.firstname = ""
		self.middlename = ""
		self.title = ""
		self.accountid = ""
		self.phone = ""
		self.mobile = ""
		self.workphone = ""
		self.fax = ""
		self.address_1 = ""
		self.address_2 = ""
		self.address_3 = ""
		self.address_4 = ""
		self.address_5 = ""
		self.location = ""
		self.notes = ""

class Invoice(object):
	class InvoiceLine(object):
		def __init__(self):
			self.invoice_line_id = None
			self.item_group_id = None
			self.item_id = None
			self.item_abbrev = None
			self.unit_price = None
			self.total = None
			self.discount = None
			self.sales_tax = None
			self.surcharge = None
			self.weight_item = None
		
		@property
		def quantity(self):
			return float(self.total) / float(self.unit_price)

	class TenderLine(object):
		def __init__(self):
			self.tender_line_id = None
			self.tender_line_type = None
			self.tender_line_amount = None
			self.tender_line_tip = None
			self.rounding_amount = None

	def __init__(self):
		self.id = None
		self.invoice_number = None
		self.outlet_id = None
		self.invoice_type = None # Invoice or Credit Note
		self.refund_note = None # Only if self.invoicetype = Credit Note
		self.account_id = None # If loyalty or charge account
		self.group_type = None # Table, Tab or Cash Sale
		self.group_id = None # If self.grouptype = Table or Tab
		self.table_number = None # If set
		self.group_name = None # If set
		self.when_invoiced = None
		self.staff_id = None # Field is whoinvoice
		self.staff_name = None # Staff Name
		self.where_invoiced = None # Terminal invoiced from

		self.invoice_lines = []
		self.subtotal = None
		self.less_discount = None # self.subtotal - discount (WTF?)
		self.food = None
		self.beverage = None
		self.balance_due = None
		self.sales_tax = None

		self.tender_lines = []
		self.tendered = None
		self.change = None
		self.on_account = None

class WizBang(object):
	def __init__(self, server_url, server_port):
		self.server_url = server_url
		self.server_port = server_port
		self.menu = self.load_menu()

	def _api_request(self, path, payload=None):
		return requests.get("http://{}:{}/{}".format(self.server_url, self.server_port, path), params=payload)

	def get_id(self, item):
		return [attr for attr in item.attrs if 'id' in attr[0]][0][1]

	def get_value(self, item, key):
		if item.find(key):
			return item.find(key).text
		return None

	def load_menu(self):
		data = self._api_request('menu.xml')
		soup = BeautifulSoup(data.text)
		menu = Menu()

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

	def place_order(self, order, customer, on_account=False):
		payload = {
			"customerid": customer.id,
			"epd": 2 if on_account else 3,
			"olcount": len(order.items),
			"tenderpayment": 0 if on_account else 1,
			"tenderaccount": 0 if on_account else 1,
		}

		if on_account:
			payload['customeraccountid'] = customer.accountid

		for n, line in enumerate(order.items):
			payload["ol{}itemid".format(n + 1)] = line['item'].id
			payload["ol{}qty".format(n + 1)] = line['quantity']

		return payload

	def get_invoice(self, id=None, number=None, outlet=None, txtcode=None):
		payload = {}
		if id is not None:
			payload['invoiceid'] = id
		elif number is not None and outlet is not None:
			payload['invoicenumber'] = number
			payload['outletid'] = outlet
		elif txtcode is not None:
			payload['txtcode'] = txtcode
		else:
			return None

		data = self._api_request('invoice', payload=payload)
		soup = BeautifulSoup(data.text)

		invoice = soup.findAll('invoice')[1]
		group = invoice.find("grouptype")
		who = group.find("whoinvoice")
		invoice_lines = group.find("invoicelines")
	
		i = Invoice()
		i.id = self.get_id(invoice)
		i.invoice_number = self.get_value(invoice, "invoiceno")
		i.outletid = self.get_value(invoice, "outletid")
		i.invoice_type = self.get_value(invoice, "invoicetype")
		i.refund_note = self.get_value(invoice, "refundnote")
		i.account_id = self.get_value(invoice, "accountid")

		i.group_type = [attr for attr in group.attrs if 'type' in attr[0]][0][1] # Yuck
		i.group_id = self.get_value(group, "groupid")
		i.table_number = self.get_value(group, "tableno")
		i.group_name = self.get_value(group, "groupname")
		i.when_invoiced = self.get_value(group, "wheninvoiced")

		i.staff_id = self.get_id(who)
		i.staff_name = self.get_value(who, "name")
		i.where_invoiced = self.get_value(who, "whereinvoiced")

		for invoice_line in invoice_lines.findAll("invoiceline"):
			l = Invoice.InvoiceLine()
			l.invoice_line_id = self.get_id(invoice_line)
			l.item_group = self.get_id(invoice_line.find("itemgroup"))
			l.item_id = self.get_id(invoice_line.find("item"))
			l.item_abbrev = self.get_value(invoice_line, "itemabbrev") 
			l.unit_price = self.get_value(invoice_line, "unitprice")
			l.total = self.get_value(invoice_line, "ilamount")
			l.discount = self.get_value(invoice_line, "discountamount")
			l.sales_tax = self.get_value(invoice_line, "salestax")
			i.invoice_lines.append(l)

		i.subtotal = self.get_value(invoice_lines, "subtotal")
		i.less_discount = self.get_value(invoice_lines, "lessdiscount")
		i.beverage = self.get_value(invoice_lines, "bev")
		i.sales_tax = self.get_value(invoice_lines, "includesgst")
		i.food = self.get_value(invoice_lines, "food")
		i.balance_due = self.get_value(invoice_lines, "balancedue")

		tender_lines = group.find("tenderlines")
		for tender_line in tender_lines.findAll("tenderline"):
			t = Invoice.TenderLine()
			t.tender_line_id = self.get_id(tender_line)
			t.tender_line_type = self.get_value(tender_line, "tenderlinetype")
			t.tender_line_amount = self.get_value(tender_line, "tenderlineamount")
			t.tender_line_tip = self.get_value(tender_line, "tenderlinetip")
			t.rounding_amount = self.get_value(tender_line, "roundingamount")
			i.tender_lines.append(t)

		i.tendered = self.get_value(tender_lines, "tendered")
		i.change = self.get_value(tender_lines, "change")
		i.on_account = self.get_value(tender_lines, "onaccount")

		return i

	@property
	def account_types(self):
		data = self._api_request('accounttypes.xml')
		soup = BeautifulSoup(data.text)

		return soup

	def order(self, customer=None, order=None, tender=None):
		return

	def get_account(self, id=None, number=None):
		return

	def get_print_messages(self, outlet=None):
		return

class Tender(object):
	def __init__(self):
		return

class Account(object):
	def __init__(self):
		return

class PrintMessages(object):
	def __init__(self):
		return