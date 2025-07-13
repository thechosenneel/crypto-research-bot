from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = "CG-oUpG62o22KvJGpmC99XE5tRz"

COINGECKO_SEARCH = "https://api.coingecko.com/api/v3/search"
COINGECKO_COIN_DATA = "https://api.coingecko.com/api/v3/coins/{}"

@app.route("/", methods=["GET", "POST"])
def index():
    coin_data = None
    error = None

    if request.method == "POST":
        search_query = request.form.get("coin_name", "").strip().lower()

        try:
            search_res = requests.get(COINGECKO_SEARCH, params={"query": search_query})
            results = search_res.json().get("coins", [])

            if not results:
                error = "No coins found. Try a different name."
            else:
                coin_id = results[0]["id"]
                data_res = requests.get(COINGECKO_COIN_DATA.format(coin_id), params={"sparkline": "true"})
                raw = data_res.json()

                market_data = raw.get("market_data", {})
                coin_data = {
                    "name": raw.get("name"),
                    "symbol": raw.get("symbol"),
                    "image": raw.get("image", {}).get("large"),
                    "price": market_data.get("current_price", {}).get("usd"),
                    "change_24h": market_data.get("price_change_percentage_24h"),
                    "change_7d": market_data.get("price_change_percentage_7d"),
                    "market_cap": market_data.get("market_cap", {}).get("usd"),
                    "volume": market_data.get("total_volume", {}).get("usd"),
                    "ath": market_data.get("ath", {}).get("usd"),
                    "ath_change": market_data.get("ath_change_percentage", {}).get("usd"),
                    "sparkline": market_data.get("sparkline_7d", {}).get("price", [])
                }
        except Exception as e:
            error = str(e)

    return render_template("index.html", coin=coin_data, error=error)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
