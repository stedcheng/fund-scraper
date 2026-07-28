from flask import Flask, jsonify, url_for
import requests
import os

app = Flask(__name__)

@app.route("/")
def home():
    sunlife = f'<a href="{url_for("get_sunlife_fund_values")}">Go to Sun Life Data</a>'
    axa = f'<a href="{url_for("get_axa_fund_values")}">Go to AXA Data</a>'
    return sunlife + "\n" + axa

@app.route("/axa")
def get_axa_fund_values():
    url = "https://www.axa.com.ph/bin/public/ecomm/fundtable/prices"
    response = requests.get(url)
    return jsonify(response.json())

@app.route("/sunlife")
def get_sunlife_fund_values():
    url = "https://www.sunlife.com.ph/funds/navprice/vul/latest"
    headers = {
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0',
    }
    params = {
        'version': '1',
        'language': 'en-us',
    }
    response = requests.post(url, params=params, headers=headers)
    return jsonify(response.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)