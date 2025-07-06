from flask import Flask, render_template
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

    try:
        response = requests.get(COINGECKO_API, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching CoinGecko data: {e}")
        return []

    filtered = []

    for coin in data:
        try:
            # Extract safely with fallback values
            market_cap = coin.get('market_cap') or 0
            volume = coin.get('total_volume') or 0
            price = coin.get('current_price') or 0
            change_24h = coin.get('price_change_percentage_24h') or 0
            change_7d = coin.get('price_change_percentage_7d_in_currency') or 0
            max_supply = coin.get('max_supply')

            # Apply core filter conditions
            if (
                market_cap < 50_000_000 and
                volume > 1_000_000 and
                2 < change_24h < 50 and
                change_7d > 0 and
                price < 2 and
                max_supply is not None
            ):
                filtered.append({
                    'name': coin.get('name'),
                    'symbol': coin.get('symbol'),
                    'price': round(price, 4),
                    'market_cap': round(market_cap),
                    'volume': round(volume),
                    'change_24h': round(change_24h, 2),
                    'change_7d': round(change_7d, 2),
                    'image': coin.get('image'),
                })

        except Exception as e:
            print(f"Error processing coin {coin.get('id')}: {e}")

    return filtered

@app.route('/')
def index():
    coins = fetch_filtered_coins()
    return render_template('index.html', coins=coins)

if __name__ == '__main__':
    app.run(debug=True)
