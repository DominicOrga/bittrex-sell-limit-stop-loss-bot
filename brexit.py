from bittrex import bittrex
import json
import time
import subprocess
import os

class Brexit(object):

	market = ""
	stop_loss = {}
	sell_limit = {}

	btx1 = None

	def __init__(self, api_key, secret_key):
		''' API_V2_0 buggy. If possible, use API_V1_1. '''
		self.btx1 = bittrex.Bittrex(api_key, secret_key, api_version = bittrex.API_V1_1)

		self.sell_limit["order_type"] = bittrex.ORDERTYPE_LIMIT		
		self.sell_limit["time_in_effect"] = bittrex.TIMEINEFFECT_GOOD_TIL_CANCELLED
		self.sell_limit["condition_type"] = bittrex.CONDITIONTYPE_LESS_THAN

		self.stop_loss["order_type"] = bittrex.ORDERTYPE_LIMIT
		self.stop_loss["time_in_effect"] = bittrex.TIMEINEFFECT_GOOD_TIL_CANCELLED
		self.stop_loss["condition_type"] = bittrex.CONDITIONTYPE_GREATER_THAN

	def check_keys(self):
		print("[Checking if keys are valid...]")
		result = self.btx1.buy_limit("USDT-BTC", -999, -999)

		if not result["success"] and result["message"] in ("APIKEY_INVALID", "INVALID_SIGNATURE"):
			print("[" + result["message"] + "]")
			return False

		return True

	def set_market(self, market):
		print("[Checking if market is valid...]")

		result = self.btx1.get_marketsummary(market)

		if result["success"]:
			print("[Market checking successful]")
			self.market = market
			return True

		print("[" + result["message"] + "]")
		return False

	def set_stop_loss(self, quantity, rate):
		test_passed = self.test_order(quantity, rate)

		if test_passed:
			self.stop_loss["quantity"] = quantity
			self.stop_loss["rate"] = rate

		return test_passed

	def set_sell_limit(self, quantity, rate):
		test_passed = self.test_order(quantity, rate)

		if test_passed:
			self.sell_limit["quantity"] = quantity
			self.sell_limit["rate"] = rate

		return test_passed

	def test_order(self, quantity, rate):
		print("[Testing order...]")

		result = self.btx1.sell_limit(self.market, quantity, rate)

		if result["success"]:
			print("[Order test successful]")

			result = self.btx1.cancel(result["result"]["uuid"])
			if not result["success"]:
				print("[Failed to remove order for {} during test. Please remove it manually.]".format(self.market))

			return True

		print("[" + result["message"] + "]")
		return False
	
#1 Check if key.json exists.
	#2 if exists, then get and test market.
	#3 Prompt user if they wish to change key.
		#4 If yes, then go to #6, else end.
	#5 if key.json does not exists,
		#6 input new api key
		#7 input new secret key
		#8 Test if new keys work
			#9 If keys does not work, go back to #6.
			#10 If keys passsed, then go to #11
		#11 Create new key.json file then save new keys.
		#12 End 

try:
	with open("key.json", "r") as in_file:
		keys = json.load(in_file)

	brexit = Brexit(keys["api"], keys["secret"])

	if not brexit.check_keys():
		raise ValueError()

	i = input("Use this key (Y = Yes, Not Y = No)? ")

	if i not in ("Y || y"):
		raise ValueError()
		
except:
	while True:
		print("\nWARNING: Make sure that the ALL permissions are enabled EXCEPT for WITHDRAW permission")
		api_key = input("Enter API key: ")
		secret_key = input("Enter Secret key: ")

		brexit = Brexit(api_key, secret_key)

		if brexit.check_keys():
			keys = {"api": api_key, "secret": secret_key}
			
			with open("key.json", "w") as out_file:
				json.dump(keys, out_file)

			print("[Key save successful.]")
			break

''' Set and test market '''
while True:
	print("\ni.e. USDT-BTC")
	market_input = input("Enter Market: ")
	market = market_input
	res = brexit.set_market(market)

	if res:
		break

'''  Set and test stop loss order '''
while True:
	print("\nWARNING: Never place a TEST RATE near the ACTUAL RATE!")
	quantity = input("Input stop loss order quantity: ")
	rate = input("Input stop loss order rate: ")

	res = brexit.set_stop_loss(quantity, rate)

	if res:
		break

''' Set and test sell limit order '''
while True:
	print("\nWARNING: Never place a TEST RATE near the ACTUAL RATE!")
	quantity = input("Input sell limit order quantity: ")
	rate = input("Input sell limit order rate: ")

	res = brexit.set_sell_limit(quantity, rate)

	if res:
		break

a = input("\nPlace stop loss and sell limit orders [Y = Yes, NOT Y = No]: ")

if a in ("Y", "y"):



	''' Write stop loss and sell limit orders in order.txt file '''
	order = { "market": brexit.market, "stop_loss": brexit.stop_loss, "sell_limit": brexit.sell_limit }
	
	with open("order.json", "w") as out_file:
		json.dump(order, out_file)

	''' Create or clear order_state.json '''
	open("order_state.json", "w").close()

	sequence = 0
	p = subprocess.Popen(["python", "subproc.py"])

	''' Check if subprocess is stuck. If stuck, then restart it '''
	while True:
		order_state = {}

		if os.path.isfile("order_state.json"):
			with open("order_state.json", "r") as in_file:
				try:
					order_state = json.load(in_file)
				except:
					pass

		if order_state:
			if int(order_state["sequence"]) == sequence:
				print("[Subprocess restarted due to stucking issue]")
				p.kill()
				p = subprocess.Popen(["python", "subproc.py"])

			sequence = order_state["sequence"]

		time.sleep(240)
else:
	print("Bye Bye")