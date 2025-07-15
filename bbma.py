import requests
from config import API_KEY

def fetch_data(symbol, interval):
    symbol = symbol.replace("/", "")
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=50&apikey={API_KEY}&indicators=ema,sma,bbands"
    resp = requests.get(url).json()
    if 'values' not in resp:
        print("API error:", resp)
        return []
    return resp['values']

def parse_indicators(data):
    prices = []
    bb_upper = []
    bb_lower = []
    ema_50 = []
    ma_5_high = []
    ma_10_high = []
    ma_5_low = []
    ma_10_low = []

    for d in data:
        prices.append(float(d['close']))
        bb_upper.append(float(d.get('upper_band', 0)))
        bb_lower.append(float(d.get('lower_band', 0)))
        ema_50.append(float(d.get('ema', 0)))
        ma_5_high.append(float(d.get('sma', 0)))
        ma_10_high.append(float(d.get('sma', 0)))
        ma_5_low.append(float(d.get('sma', 0)))
        ma_10_low.append(float(d.get('sma', 0)))

    return {
        "prices": prices,
        "bb_upper": bb_upper,
        "bb_lower": bb_lower,
        "ema_50": ema_50,
        "ma_5_high": ma_5_high,
        "ma_10_high": ma_10_high,
        "ma_5_low": ma_5_low,
        "ma_10_low": ma_10_low,
    }

def detect_signal(parsed_data):
    if len(parsed_data["prices"]) < 2:
        return None

    price_now = parsed_data["prices"][0]
    ma5_high = parsed_data["ma_5_high"][0]
    bb_upper = parsed_data["bb_upper"][0]

    if price_now > ma5_high and price_now > bb_upper:
        return "📈 Momentum Buy"

    elif price_now < parsed_data["ma_5_low"][0] and price_now < parsed_data["bb_lower"][0]:
        return "📉 Momentum Sell"

    return None