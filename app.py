import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Function to fetch top 7 coins
def fetch_top_coins():
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
            'current_price': coin.get('current_price'),
            'market_cap': coin.get('market_cap'),
            'price_change_percentage_24h': coin.get('price_change_percentage_24h'),
            'image': coin.get('image')
        })
    return coins

@app.route('/')
def index():
    coins = fetch_top_coins()
    return render_template('index.html', coins=coins)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    url = f'https://api.coingecko.com/api/v3/search?query={query}'
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return jsonify(data.get('coins', []))
    except Exception as e:
        print(f"[SEARCH ERROR] {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
