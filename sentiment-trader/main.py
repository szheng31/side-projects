import requests
from dotenv import load_dotenv
import os
from google import genai
import json
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import GetAssetsRequest
from alpaca_trade_api.rest import REST

import time

load_dotenv()
NYTIMESKEY = os.getenv("NYTIMESKEY")
GOOGLEAPIKEY = os.getenv("GOOGLEAPIKEY")
ALPACA = os.getenv("ALPACA")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")


def promptter(prompt):

    client = genai.Client(api_key=GOOGLEAPIKEY)
    r = None
    response = client.models.generate_content(model="gemini-2.5-flash",
                                              contents=prompt)
    
    while r is None:
        try:
            
            r = json.loads(response.text)
        except:
            time.sleep(0.5)
            response = client.models.generate_content(model="gemini-2.5-flash",
                                                      contents=prompt)

    return r

def place_market_buy_order(symbol, quantity):
    market_order_data = MarketOrderRequest(symbol=symbol,
                                           qty=quantity,
                                           side=OrderSide.BUY,
                                           time_in_force=TimeInForce.DAY)
    market_order = trading_client.submit_order(order_data=market_order_data)
    return True

def place_market_sell_order(symbol, quantity):
    market_order_data = MarketOrderRequest(symbol=symbol,
                                           qty=quantity,
                                           side=OrderSide.SELL,
                                           time_in_force=TimeInForce.DAY)
    market_order = trading_client.submit_order(order_data=market_order_data)
    return True

# format stock_tickers.json
with open('stock_tickers.json', 'r') as file:
    tickers = json.load(file)

tickers.pop("NaN")
r = requests.get(
    f"https://api.nytimes.com/svc/topstories/v2/home.json?api-key={NYTIMESKEY}"
)

results = r.json()["results"]

#parse results
titles = [i["title"] for i in results]

abstract = [i["abstract"] for i in results]

print("NYTIMES scrapping done.")



prompt = f"""
You are a neutral, fact-based analyst. You are 
given a list of daily cover stories,
 each with a title and abstract. Based on their content, 
 identify which industries are likely to be affected by the news. 
 Your analysis should be unbiased and focus on sectors impacted economically,
   politically, socially, or technologically.
The only industries you can identify are {", ".join(tickers.keys())}.
Do not create or use any new industries. If none apply, exclude them.
The titles are the following: {", ".join(titles)}.
The abstracts, which are corresponding to the titles are the following: {", ".join(abstract)}
Return the results in the following format without an explanation, only the list: 
{{"industry": "positive/negative", ...}}, and make sure there is no formatting

"""
print("prompting")
industries = promptter(prompt)
print("recieved prompt")
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(ALPACA, ALPACA_SECRET, BASE_URL)
positions = api.list_positions()

p = {}
for position in positions:
    p[position.symbol] = position
trading_client = TradingClient(ALPACA, ALPACA_SECRET, paper=True)





for industry in industries.keys():
    try:
        stocks = tickers[industry]
        sentiment = industries[industry]
        if sentiment == "positive":
            for stock in stocks:
                if stock in p and p[stock].unrealized_pl > 0:  # basic sell if sentiment is positive
                    place_market_sell_order(stock, p[stock].qty)
                else:
                    place_market_buy_order(stock, 1)
            time.sleep(0.5)
        else: # negative sentiment
           for stock in stocks: #sentiment 
                if stock in p and p[stock].unrealized_pl > 0:  # basic sell if sentiment is negative
                    place_market_sell_order(stock, p[stock].qty)
                elif stock in p and p[stock].unrealized_pl < 0:  # explicit basic sell if sentiment is negative
                    place_market_buy_order(stock, 1)  
                else: # if we don't have, let's buy some YOLO
                    place_market_buy_order(stock, 1)
                    

    except:
        print("ai hallucination")
