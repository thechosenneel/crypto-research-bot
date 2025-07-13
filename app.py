# app.py
from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching

# CoinGecko API endpoints
SEARCH_URL = "https://api.coingecko.com/api/v3/search?query={}"
COIN_DETAILS_URL = "https://api.coingecko.com/api/v3/coins/{}?localization=false&sparkline=true"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_coins():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
    
    try:
        response = requests.get(SEARCH_URL.format(query))
        response.raise_for_status()
        coins = response.json().get('coins', [])
        
        # Format results for autocomplete
        results = [{
            'id': coin['id'],
            'name': coin['name'],
            'symbol': coin['symbol'],
            'label': f"{coin['name']} ({coin['symbol'].upper()})"
        } for coin in coins[:7]]  # Limit to 7 results
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/coin/<coin_id>')
def get_coin_details(coin_id):
    try:
        response = requests.get(COIN_DETAILS_URL.format(coin_id))
        response.raise_for_status()
        data = response.json()
        
        # Extract required data
        market_data = data['market_data']
        sparkline = market_data['sparkline_7d']['price']
        
        # Calculate additional metrics
        volume_mc_ratio = (market_data['total_volume']['usd'] / 
                          market_data['market_cap']['usd']) * 100 if market_data['market_cap']['usd'] else 0
        
        ath_gap = ((market_data['ath']['usd'] - market_data['current_price']['usd']) / 
                  market_data['ath']['usd']) * 100 if market_data['ath']['usd'] else 0
        
        circulating_percent = (data['market_data']['circulating_supply'] / 
                             data['market_data']['total_supply']) * 100 if data['market_data']['total_supply'] else 100
        
        return jsonify({
            'name': data['name'],
            'symbol': data['symbol'].upper(),
            'current_price': market_data['current_price']['usd'],
            'price_change_24h': market_data['price_change_percentage_24h_in_currency']['usd'],
            'price_change_7d': market_data['price_change_percentage_7d_in_currency']['usd'],
            'market_cap': market_data['market_cap']['usd'],
            'volume_24h': market_data['total_volume']['usd'],
            'market_cap_rank': data['market_cap_rank'],
            'volume_mc_ratio': volume_mc_ratio,
            'ath_gap': ath_gap,
            'circulating_percent': circulating_percent,
            'sparkline': sparkline
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
