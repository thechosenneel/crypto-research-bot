from flask import Flask, render_template, request
import requests

app = Flask(__name__)

COINGECKO_API = 'https://api.coingecko.com/api/v3/coins/markets'

def fetch_filtered_coins():
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_asc',
        'per_page': 250,
        'page': 1,
        'price_change_percentage': '24h,7d'
    }

    response = requests.get(COINGECKO_API, params=params)
    data = response.json()

    filtered = []

    for coin in data:
        try:
            market_cap = coin['market_cap'] or 0
            volume = coin['total_volume'] or 0
            price = coin['current_price'] or 0
            change_24h = coin['price_change_percentage_24h'] or 0
            change_7d = coin.get('price_change_percentage_7d_in_currency', 0)
            max_supply = coin['max_supply']

            if (
                market_cap < 50000000 and
                volume > 1000000 and
                2 < change_24h < 50 and
                change_7d > 0 and
                price < 2 and
                max_supply is not None
            ):
                filtered.append({
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'price': price,
                    'market_cap': market_cap,
                    'volume': volume,
                    'change_24h': change_24h,
                    'change_7d': change_7d,
                    'image': coin['image']
                })

        except Exception as e:
            print(f"Error processing coin: {coin.get('id')} → {e}")

    return filtered

@app.route('/', methods=['GET'])
def index():
    coins = fetch_filtered_coins()
    return render_template('index.html', coins=coins)

if __name__ == '__main__':
    app.run(debug=True)
