# app.py
from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# CoinGecko API configuration
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')
HEADERS = {'X-CG-Pro-API-Key': COINGECKO_API_KEY} if COINGECKO_API_KEY else {}

SEARCH_URL = "https://api.coingecko.com/api/v3/search?query={}"
COIN_DETAILS_URL = "https://api.coingecko.com/api/v3/coins/{}?localization=false&sparkline=true"

def make_coingecko_request(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"CoinGecko API error: {e}")
        return None
    except ValueError as e:
        app.logger.error(f"JSON decode error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html', has_api_key=bool(COINGECKO_API_KEY))

@app.route('/search')
def search_coins():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
    
    try:
        data = make_coingecko_request(SEARCH_URL.format(query))
        if data is None:
            return jsonify({'error': 'Failed to fetch data from CoinGecko'}), 500
        
        coins = data.get('coins', [])
        
        results = [{
            'id': coin['id'],
            'name': coin['name'],
            'symbol': coin['symbol']
        } for coin in coins[:7]]
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/coin/<coin_id>')
def get_coin_details(coin_id):
    try:
        data = make_coingecko_request(COIN_DETAILS_URL.format(coin_id))
        if data is None:
            return jsonify({'error': 'Failed to fetch coin data'}), 500
        
        market_data = data.get('market_data', {})
        if not market_data:
            return jsonify({'error': 'Market data not available for this coin'}), 400
        
        # Extract required data
        current_price = market_data.get('current_price', {}).get('usd')
        price_change_24h = market_data.get('price_change_percentage_24h_in_currency', {}).get('usd')
        price_change_7d = market_data.get('price_change_percentage_7d_in_currency', {}).get('usd')
        market_cap = market_data.get('market_cap', {}).get('usd')
        volume_24h = market_data.get('total_volume', {}).get('usd')
        market_cap_rank = data.get('market_cap_rank')
        ath = market_data.get('ath', {}).get('usd')
        
        # Calculate additional metrics
        volume_mc_ratio = (volume_24h / market_cap * 100) if market_cap and market_cap > 0 else 0
        ath_gap = ((ath - current_price) / ath * 100) if ath and ath > 0 else 0
        
        circulating_supply = market_data.get('circulating_supply')
        total_supply = market_data.get('total_supply')
        circulating_percent = (circulating_supply / total_supply * 100) if total_supply and total_supply > 0 else 100
        
        sparkline = market_data.get('sparkline_7d', {}).get('price', [])
        
        return jsonify({
            'name': data.get('name', 'Unknown'),
            'symbol': data.get('symbol', '').upper(),
            'current_price': current_price,
            'price_change_24h': price_change_24h,
            'price_change_7d': price_change_7d,
            'market_cap': market_cap,
            'volume_24h': volume_24h,
            'market_cap_rank': market_cap_rank,
            'volume_mc_ratio': volume_mc_ratio,
            'ath_gap': ath_gap,
            'circulating_percent': circulating_percent,
            'sparkline': sparkline
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
