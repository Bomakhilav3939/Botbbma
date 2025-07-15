import os, time, requests
import pandas as pd
from dotenv import load_dotenv
import telegram
import ta

load_dotenv()
API_KEY = os.getenv("TWELVE_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOLS = os.getenv("SYMBOLS", "XAU/USD").split(",")

bot = telegram.Bot(token=BOT_TOKEN)

INTERVALS = {
    "15min": "M15",
    "1h": "H1",
    "4h": "H4"
}

def fetch_data(symbol, interval):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol.strip()}&interval={interval}&outputsize=100&apikey={API_KEY}"
    r = requests.get(url).json()
    if 'values' not in r:
        print(f"[ERROR] Failed to get {symbol} {interval}: {r}")
        return None
    df = pd.DataFrame(r['values'])
    df = df.astype(float)
    df = df[::-1]  # urutkan dari lama ke terbaru
    return df

def apply_indicators(df):
    df['ma5_high'] = df['high'].rolling(5).mean()
    df['ma5_low'] = df['low'].rolling(5).mean()
    df['ma10_high'] = df['high'].rolling(10).mean()
    df['ma10_low'] = df['low'].rolling(10).mean()
    bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['ema50'] = ta.trend.ema_indicator(df['close'], 50)
    return df

def detect_signals(df, symbol, tf):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    signals = []

    if prev['close'] < prev['ma5_high'] and latest['close'] > latest['ma5_high']:
        signals.append("📈 MOMENTUM BUY")
    elif prev['close'] > prev['ma5_low'] and latest['close'] < latest['ma5_low']:
        signals.append("📉 MOMENTUM SELL")

    if latest['close'] > latest['ma5_low'] and latest['close'] < latest['ma10_low'] and latest['close'] > latest['ema50']:
        signals.append("🔁 REENTRY BUY")
    elif latest['close'] < latest['ma5_high'] and latest['close'] > latest['ma10_high'] and latest['close'] < latest['ema50']:
        signals.append("🔁 REENTRY SELL")

    return signals

def send_signal(text):
    bot.send_message(chat_id=CHAT_ID, text=text)
    print(text)

def run():
    for symbol in SYMBOLS:
        for interval, tf_label in INTERVALS.items():
            df = fetch_data(symbol, interval)
            if df is None:
                continue
            df = apply_indicators(df)
            signals = detect_signals(df, symbol, tf_label)
            for signal in signals:
                msg = f"{signal}\nPair: {symbol}\nTimeframe: {tf_label}\nPrice: {df.iloc[-1]['close']:.2f}"
                send_signal(msg)

if __name__ == "__main__":
    while True:
        run()
        time.sleep(900)
