from flask import Flask, render_template
import requests
import os

app = Flask(__name__)  # <- This is the 'app' that Gunicorn needs

def fetch_filtered_coins():
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 7,
        'page': 1,
        'price_change_percentage': '24h,7d'
    }

    headers = {
        'x-cg-pro-api-key': os.getenv("COINGECKO_API")
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch from CoinGecko: {e}")
        return []

    coins = []

    for coin in data:
        coins.append({
            'name': coin.get('name'),
            'symbol': coin.get('symbol'),
            'price': round(coin.get('current_price', 0), 4),
            'market_cap': round(coin.get('market_cap', 0)),
            'volume': round(coin.get('total_volume', 0)),
            'change_24h': round(coin.get('price_change_percentage_24h', 0), 2),
            'change_7d': round(coin.get('price_change_percentage_7d_in_currency', 0), 2),
            'image': coin.get('image'),
        })

    return coins

@app.route('/')
def index():
    coins = fetch_filtered_coins()
    return render_template('index.html', coins=coins)

if __name__ == '__main__':
    app.run(debug=True)
