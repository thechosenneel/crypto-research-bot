from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

COINGECKO_API_KEY = os.getenv("COINGECKO_API")

@app.route('/')
def index():
    coins = fetch_top_coins()
    return render_template('index.html', coins=coins)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = []

    if not query:
        return jsonify(results)

    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/search',
            headers={'x-cg-pro-api-key': COINGECKO_API_KEY}
        )
        data = response.json()
        for coin in data.get('coins', []):
            if query in coin['name'].lower() or query in coin['symbol'].lower():
                results.append({
                    'id': coin['id'],
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'thumb': coin['thumb']
                })
    except Exception as e:
        print(f"[ERROR] Coin search failed: {e}")

    return jsonify(results)

@app.route('/coin/<coin_id>')
def coin_details(coin_id):
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
        response = requests.get(url, headers={'x-cg-pro-api-key': COINGECKO_API_KEY})
        data = response.json()
        return render_template('coin.html', coin=data)
    except Exception as e:
        print(f"[ERROR] Coin detail fetch failed: {e}")
        return "Coin not found", 404

def fetch_top_coins():
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 7,
            'page': 1
        }
        response = requests.get(url, params=params, headers={'x-cg-pro-api-key': COINGECKO_API_KEY})
        return response.json()
    except:
        return []

if __name__ == '__main__':
    app.run(debug=True)
