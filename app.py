from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

COINGECKO_API_KEY = os.getenv("COINGECKO_API")

def fetch_filtered_coins():
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_asc',
        'per_page': 250,
        'page': 1,
        'price_change_percentage': '24h,7d'
    }

    headers = {
        'x-cg-pro-api-key': COINGECKO_API_KEY
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch from CoinGecko: {e}")
        data = []

    filtered = []

    for coin in data:
        try:
            market_cap = coin.get('market_cap', 0)
            volume = coin.get('total_volume', 0)
            price = coin.get('current_price', 0)
            change_24h = coin.get('price_change_percentage_24h', 0)
            change_7d = coin.get('price_change_percentage_7d_in_currency', 0)
            max_supply = coin.get('max_supply')

            if (
                market_cap < 150_000_000 and
                volume > 500_000 and
                1 < change_24h < 80 and
                change_7d > 0 and
                price < 2 and
                max_supply is not None
            ):
                filtered.append({
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'price': round(price, 4),
                    'market_cap': round(market_cap),
                    'volume': round(volume),
                    'change_24h': round(change_24h, 2),
                    'change_7d': round(change_7d, 2),
                    'image': coin['image'],
                })

        except Exception as e:
            print(f"[SKIP] Error parsing coin: {coin.get('id')} → {e}")

    return filtered

@app.route('/')
def index():
    coins = fetch_filtered_coins()
    return render_template('index.html', coins=coins)

if __name__ == '__main__':
    app.run(debug=True)
