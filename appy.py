import os, time
from datetime import datetime, timezone
from heapq import heappush, heappushpop
import pandas as pd
import yfinance as yf
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DEFAULT_TICKERS = os.environ.get("TICKERS", "AAPL,MSFT,AMZN,GOOGL,NVDA,TSLA").split(",")
CACHE_SECONDS = int(os.environ.get("CACHE_SECONDS", "60"))

_last_fetch = 0.0
_cached_closes = None
_cached_vols = None

def fetch_prices(tickers, period="1d", interval="5m"):
    data = yf.download(tickers=tickers, period=period, interval=interval,
                       auto_adjust=True, progress=False, threads=True)
    if isinstance(data.columns, pd.MultiIndex):
        closes = data["Close"]
        vols = data["Volume"]
    else:
        closes = data["Close"].to_frame(name=tickers[0])
        vols = data["Volume"].to_frame(name=tickers[0])
    return closes.dropna(how="all"), vols.dropna(how="all")

def ensure_data(tickers, period="1d", interval="5m"):
    global _last_fetch, _cached_closes, _cached_vols
    now = time.time()
    if (now - _last_fetch) > CACHE_SECONDS or _cached_closes is None:
        closes, vols = fetch_prices(tickers, period, interval)
        _cached_closes, _cached_vols = closes, vols
        _last_fetch = now
    return _cached_closes, _cached_vols

def top_n_by_change(closes, n=5):
    heap = []
    for t in closes.columns:
        s = closes[t].dropna()
        if len(s) < 2: continue
        change = (s.iloc[-1] - s.iloc[0]) / s.iloc[0] * 100
        if len(heap) < n:
            heappush(heap, (change, t))
        else:
            if change > heap[0][0]:
                heappushpop(heap, (change, t))
    return sorted(heap, reverse=True)

@app.route("/")
def home():
    return render_template("index.html", default_tickers=",".join(DEFAULT_TICKERS))

@app.route("/api/top")
def api_top():
    n = int(request.args.get("n", 5))
    tickers = request.args.get("tickers", ",".join(DEFAULT_TICKERS)).split(",")
    closes, vols = ensure_data(tickers)
    top = top_n_by_change(closes, n)
    return jsonify({"top": [{"ticker": t, "change": round(c,2)} for c,t in top]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
