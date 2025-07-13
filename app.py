from flask import Flask, render_template
import requests

app = Flask(__name__)

API_KEY = "CG-oUpG62o22KvJGpmC99XE5tRz"

def fetch_filtered_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    headers = {
        "x-cg-demo-api-key": API_KEY
    }
    params = {
        "vs_currency": "usd",
        "order": "market_cap_asc",
        "per_page": 100,
        "page": 1,
        "sparkline": "true",
        "price_change_percentage": "24h,7d"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    result = []

    for coin in data:
        try:
            vol = coin['total_volume']
            cap = coin['market_cap']
            price = coin['current_price']
            ath = coin['ath']
            circ = coin.get('circulating_supply', 0)
            total = coin.get('total_supply', 1)
            rank = coin.get('market_cap_rank', 9999)

            if cap == 0 or total == 0 or ath == 0:
                continue

            vol_to_cap = vol / cap
            ath_gap = ((ath - price) / ath) * 100
            circ_percent = (circ / total) * 100

            if (
                price < 1 and
                vol > 1_000_000 and
                vol_to_cap > 1 and
                circ_percent > 50 and
                ath_gap > 40 and
                rank < 300
            ):
                result.append({
                    "name": coin['name'],
                    "symbol": coin['symbol'],
                    "image": coin['image'],
                    "price": price,
                    "volume": vol,
                    "market_cap": cap,
                    "rank": rank,
                    "volume_to_cap": round(vol_to_cap, 2),
                    "ath_gap_percent": round(ath_gap, 2),
                    "circ_supply_percent": round(circ_percent, 2),
                    "change_24h": coin.get("price_change_percentage_24h_in_currency"),
                    "change_7d": coin.get("price_change_percentage_7d_in_currency"),
                    "sparkline": coin.get("sparkline_in_7d", {}).get("price", [])
                })
        except:
            continue

    return result

@app.route("/")
def index():
    try:
        coins = fetch_filtered_coins()
        return render_template("index.html", coins=coins)
    except Exception as e:
        return render_template("index.html", coins=[], error=str(e))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
