from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("COINGECKO_API", "CG-oUpG62o22KvJGpmC99XE5tRz")
BASE_URL = "https://api.coingecko.com/api/v3"


@app.route("/")
def home():
    return render_template("index.html", coins=[], error=None)


@app.route("/search")
def search():
    query = request.args.get("query", "")
    if not query:
        return jsonify([])

    url = f"{BASE_URL}/search?query={query}"
    try:
        res = requests.get(url)
        data = res.json()
        coins = data.get("coins", [])
        suggestions = [{"id": c["id"], "name": c["name"]} for c in coins[:10]]
        return jsonify(suggestions)
    except:
        return jsonify([])


@app.route("/coin")
def coin():
    coin_id = request.args.get("id")
    if not coin_id:
        return render_template("index.html", coins=[], error="No coin selected.")

    try:
        market_data = requests.get(f"{BASE_URL}/coins/markets", params={
            "vs_currency": "usd",
            "ids": coin_id,
            "sparkline": "true",
            "price_change_percentage": "24h,7d"
        }).json()[0]

        coin = {
            "name": market_data["name"],
            "symbol": market_data["symbol"],
            "image": market_data["image"],
            "price": market_data["current_price"],
            "change_24h": round(market_data.get("price_change_percentage_24h", 0), 2),
            "change_7d": round(market_data.get("price_change_percentage_7d_in_currency", 0), 2),
            "market_cap": market_data["market_cap"],
            "volume": market_data["total_volume"],
            "rank": market_data["market_cap_rank"],
            "volume_to_cap": round(market_data["total_volume"] / market_data["market_cap"], 2),
            "ath_gap_percent": round(100 * (1 - market_data["current_price"] / market_data["ath"]), 2),
            "circ_supply_percent": round((market_data["circulating_supply"] / market_data.get("max_supply", market_data["circulating_supply"])) * 100, 2),
            "sparkline": market_data["sparkline_in_7d"]["price"]
        }

        return render_template("index.html", coins=[coin], error=None)
    except Exception as e:
        return render_template("index.html", coins=[], error="API error or coin not found.")


if __name__ == "__main__":
    app.run(debug=True)
