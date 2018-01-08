from bittrex import bittrex
from datetime import datetime
import json
import time
import os

with open("key.json", "r") as in_file:
	keys = json.load(in_file)
	api_key = keys["api"]
	secret_key = keys["secret"]

btx1 = bittrex.Bittrex(api_key, secret_key, api_version = bittrex.API_V1_1)
btx2 = bittrex.Bittrex(api_key, secret_key, api_version = bittrex.API_V2_0)

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
			result = btx2.trade_sell(
				order["market"], 
				bittrex.ORDERTYPE_LIMIT, 
				order["stop_loss"]["quantity"], 
				order["stop_loss"]["rate"], 
				bittrex.TIMEINEFFECT_GOOD_TIL_CANCELLED, 
				bittrex.CONDITIONTYPE_LESS_THAN)

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()

			print("[{} | Stop loss order set]".format(datetime.now()))

			order_state = {
				"sequence": 1,
				"OrderId": result["result"]["OrderId"],
				"state": ORDERSTATE_STOP_LOSS
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)


		elif order_state["state"] != ORDERSTATE_STOP_LOSS:
			result = btx1.cancel(order_state["OrderId"])

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()	
				
			result = btx2.trade_sell(
				order["market"], 
				bittrex.ORDERTYPE_LIMIT, 
				order["stop_loss"]["quantity"], 
				order["stop_loss"]["rate"], 
				bittrex.TIMEINEFFECT_GOOD_TIL_CANCELLED, 
				bittrex.CONDITIONTYPE_LESS_THAN)				

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()

			print("[{} | Stop loss order replaced sell limit order]".format(datetime.now()))

			order_state = {
				"sequence": int(order_state["sequence"]) + 1,
				"OrderId": result["result"]["OrderId"],
				"state": ORDERSTATE_STOP_LOSS
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)
		
		else:
			order_state = {
				"sequence": int(order_state["sequence"]) + 1,
				"OrderId": order_state["OrderId"],
				"state": order_state["state"]
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)

			print("[{} | Stop loss order already set]".format(datetime.now()))

	else:
		if not order_state:
			result = btx2.trade_sell(
				order["market"], 
				bittrex.ORDERTYPE_LIMIT, 
				order["stop_loss"]["quantity"], 
				order["stop_loss"]["rate"], 
				bittrex.TIMEINEFFECT_GOOD_TIL_CANCELLED, 
				bittrex.CONDITIONTYPE_GREATER_THAN)

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()

			print("[{} | Sell limit order set]".format(datetime.now()))

			order_state = {
				"sequence": 1,
				"OrderId": result["result"]["OrderId"],
				"state": ORDERSTATE_SELL_LIMIT
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)

		elif order_state["state"] != ORDERSTATE_SELL_LIMIT:
			result = btx1.cancel(order_state["OrderId"])

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()	
				
			result = btx2.trade_sell(
				order["market"], 
				bittrex.ORDERTYPE_LIMIT, 
				order["stop_loss"]["quantity"], 
				order["stop_loss"]["rate"], 
				bittrex.TIMEINEFFECT_GOOD_TIL_CANCELLED, 
				bittrex.CONDITIONTYPE_GREATER_THAN)

			if not result["success"]:
				print("[" + result["message"] + "]")
				quit()

			print("[{} | Sell limit order replaced stop loss order]".format(datetime.now()))

			order_state = {
				"sequence": int(order_state["sequence"]) + 1,
				"OrderId": result["result"]["OrderId"],
				"state": ORDERSTATE_SELL_LIMIT
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)

		else:
			order_state = {
				"sequence": int(order_state["sequence"]) + 1,
				"OrderId": order_state["OrderId"],
				"state": order_state["state"]
			}

			with open("order_state.json", "w") as out_file:
				json.dump(order_state, out_file)

			print("[{} | Sell limit order already set]".format(datetime.now()))

	time.sleep(60)