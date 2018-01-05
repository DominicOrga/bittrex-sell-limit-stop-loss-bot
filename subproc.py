import json
import time
import os
from datetime import datetime
from bittrex import bittrex

BITTREX_API_KEY = "ea45c56b7f0e47a2986a9f9d87e3535a"
BITTREX_SECRET_KEY = "d4ec07c80c084c2992d3a0ba1fa46a51"
btx1 = bittrex.Bittrex(BITTREX_API_KEY, BITTREX_SECRET_KEY, api_version = bittrex.API_V1_1)

ORDERSTATE_SELL_LIMIT = "ORDERSTATE_SELL_LIMIT"
ORDERSTATE_STOP_LOSS = "ORDERSTATE_STOP_LOSS"

with open("order.json", "r") as in_file:
	order = json.load(in_file)

while True:
	''' Identify which order rate is nearer to the last price of the market '''
	result = btx1.get_marketsummary(order["market"])

	if not result["success"]:
		print("[" + result["message"] + "]")
		quit()

	last_price = result["result"][0]["Last"]

	stoploss_lastprice_diff = abs(float(order["stop_loss"]["rate"]) - last_price)
	selllimit_lastprice_diff = abs(float(order["sell_limit"]["rate"]) - last_price)

	order_state = {}

	if os.path.isfile("order_state.json"):
		with open("order_state.json", "r") as in_file:
			try:
				order_state = json.load(in_file)
			except:
				pass

	if stoploss_lastprice_diff < selllimit_lastprice_diff:
		
		''' If order_state.json does not contain any json strings '''
		if not order_state:
			result = btx1.sell_limit(order["market"], order["stop_loss"]["quantity"], order["stop_loss"]["rate"])

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()

			print("[{} | Stop loss order set]".format(datetime.now()))

			order_state = {
				"sequence": 1,
				"uuid": result["result"]["uuid"],
				"state": ORDERSTATE_STOP_LOSS
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)


		elif order_state["state"] != ORDERSTATE_STOP_LOSS:
			result = btx1.cancel(order_state["uuid"])

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()	
				
			result = btx1.sell_limit(order["market"], order["stop_loss"]["quantity"], order["stop_loss"]["rate"])

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()

			print("[{} | Stop loss order replaced sell limit order]".format(datetime.now()))

			order_state = {
				"sequence": int(order_state["sequence"]) + 1,
				"uuid": result["result"]["uuid"],
				"state": ORDERSTATE_STOP_LOSS
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)
		
		else:
			order_state = {
				"sequence": int(order_state["sequence"]) + 1,
				"uuid": order_state["uuid"],
				"state": order_state["state"]
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)

			print("[{} | Stop loss order already set]".format(datetime.now()))

	else:
		if not order_state:
			result = btx1.sell_limit(order["market"], order["sell_limit"]["quantity"], order["sell_limit"]["rate"])

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()

			print("[{} | Sell limit order set]".format(datetime.now()))

			order_state = {
				"sequence": 1,
				"uuid": result["result"]["uuid"],
				"state": ORDERSTATE_SELL_LIMIT
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)

		elif order_state["state"] != ORDERSTATE_SELL_LIMIT:
			result = btx1.cancel(order_state["uuid"])

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()	
				
			result = btx1.sell_limit(order["market"], order["sell_limit"]["quantity"], order["sell_limit"]["rate"])

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()

			print("[{} | Sell limit order replaced stop loss order]".format(datetime.now()))

			order_state = {
				"sequence": int(order_state["sequence"]) + 1,
				"uuid": result["result"]["uuid"],
				"state": ORDERSTATE_SELL_LIMIT
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)

		else:
			order_state = {
				"sequence": int(order_state["sequence"]) + 1,
				"uuid": order_state["uuid"],
				"state": order_state["state"]
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)

			print("[{} | Sell limit order already set]".format(datetime.now()))

	time.sleep(60)