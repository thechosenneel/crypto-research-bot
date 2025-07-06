from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("COINGECKO_API_KEY")
BASE_URL = "https://api.coingecko.com/api/v3/coins/"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/coin_info', methods=['POST'])
def coin_info():
    coin = request.json.get("coin", "bitcoin").lower()
    url = f"{BASE_URL}{coin}"
    params = {
        "x_cg_demo_api_key": API_KEY,
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        info = {
            "name": data.get("name"),
            "image": data.get("image", {}).get("thumb"),
            "price": data.get("market_data", {}).get("current_price", {}).get("usd"),
            "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
            "volume": data.get("market_data", {}).get("total_volume", {}).get("usd"),
            "change_24h": data.get("market_data", {}).get("price_change_percentage_24h")
        }
        return jsonify(info)
    return jsonify({"error": "Coin not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
