# app.py
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("COINGECKO_API_KEY") or "CG-oUpG62o22KvJGpmC99XE5tRz"

HEADERS = {
    "accept": "application/json",
    "x-cg-pro-api-key": API_KEY
}

BASE_URL = "https://api.coingecko.com/api/v3"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    res = requests.get(f"{BASE_URL}/search?query={query}", headers=HEADERS)
    if res.status_code != 200:
        return jsonify([])
    data = res.json().get("coins", [])
    results = [{"id": c['id'], "name": c['name'], "symbol": c['symbol']} for c in data]
    return jsonify(results)

@app.route('/coin/<coin_id>')
def coin_detail(coin_id):
    try:
        detail = requests.get(f"{BASE_URL}/coins/{coin_id}?sparkline=true", headers=HEADERS).json()

        market_data = detail['market_data']
        supply = detail['market_data'].get("circulating_supply", 0)
        max_supply = detail['market_data'].get("max_supply", 1)

        coin = {
            "name": detail['name'],
            "symbol": detail['symbol'],
            "image": detail['image']['large'],
            "price": market_data['current_price']['usd'],
            "change_24h": market_data['price_change_percentage_24h'],
            "change_7d": market_data['price_change_percentage_7d'],
            "market_cap": market_data['market_cap']['usd'],
            "volume": market_data['total_volume']['usd'],
            "rank": detail['market_cap_rank'],
            "volume_to_cap": round(market_data['total_volume']['usd'] / market_data['market_cap']['usd'], 2) if market_data['market_cap']['usd'] else 0,
            "ath_gap_percent": round(100 - (market_data['current_price']['usd'] / market_data['ath']['usd']) * 100, 2),
            "circ_supply_percent": round((supply / max_supply) * 100, 2) if max_supply else 0,
            "sparkline": market_data['sparkline_7d']['price']
        }

        return render_template("index.html", coin=coin)
    except Exception as e:
        return render_template("index.html", error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
