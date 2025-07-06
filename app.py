from flask import Flask, render_template, request, jsonify
import requests
import os
API_KEY = os.getenv("COINGECKO_API_KEY")

app = Flask(__name__)

BASE_URL = "https://api.coingecko.com/api/v3/simple/price"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_price', methods=['POST'])
def get_price():
    coin = request.json.get("coin", "bitcoin")
    params = {
        "ids": coin,
        "vs_currencies": "usd",
        "x_cg_demo_api_key": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        price = data.get(coin, {}).get("usd", "N/A")
        return jsonify({"price": price})
    return jsonify({"error": "Failed to fetch price"}), 400

if __name__ == '__main__':
    app.run(debug=True)

