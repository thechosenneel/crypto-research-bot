# app.py
import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

HEADERS = {
    "accept": "application/json"
}

@app.route("/")
def index():
    return render_template("index.html", coin=None)

@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    url = "https://api.coingecko.com/api/v3/search"
    response = requests.get(url, headers=HEADERS, params={"query": query})

    if response.status_code != 200:
        return jsonify([])

    results = response.json().get("coins", [])
    suggestions = [{"id": coin["id"], "name": coin["name"], "symbol": coin["symbol"]} for coin in results]
    return jsonify(suggestions)

@app.route("/coin/<coin_id>")
def coin_details(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    params = {
        "localization": "false",
        "sparkline": "true"
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        market = data.get("market_data", {})
        if not market:
            return render_template("index.html", error="No market data found for this coin.", coin=None)

        supply = market.get("circulating_supply", 1)
        max_supply = market.get("max_supply", supply or 1)

        coin = {
            "name": data["name"],
            "symbol": data["symbol"],
            "image": data["image"]["large"],
            "price": market["current_price"]["usd"],
            "change_24h": market.get("price_change_percentage_24h", 0),
            "change_7d": market.get("price_change_percentage_7d", 0),
            "market_cap": market["market_cap"]["usd"],
            "volume": market["total_volume"]["usd"],
            "rank": data.get("market_cap_rank", "N/A"),
            "volume_to_cap": round(market["total_volume"]["usd"] / market["market_cap"]["usd"], 3) if market["market_cap"]["usd"] else 0,
            "ath_gap_percent": round(100 - ((market["current_price"]["usd"] / market["ath"]["usd"]) * 100), 2) if market["ath"]["usd"] else 0,
            "circ_supply_percent": round((supply / max_supply) * 100, 2) if max_supply else 100,
            "sparkline": market["sparkline_7d"]["price"]
        }

        return render_template("index.html", coin=coin)

    except Exception as e:
        print("ERROR:", e)
        return render_template("index.html", error="Failed to fetch coin details.", coin=None)

if __name__ == "__main__":
    app.run(debug=True)
