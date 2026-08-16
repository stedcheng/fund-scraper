from flask import Blueprint, jsonify, render_template, Response
import requests
import pandas as pd

bdo_bp = Blueprint("bdo", __name__, url_prefix = "/bdo")

@bdo_bp.route("/")
def bdo_landing_page():
    links = [
        {"name": "JSON", "url": "/bdo/json"},
        {"name": "CSV", "url": "/bdo/csv"},
        {"name": "Table", "url": "/bdo/table"}
    ]
    return render_template("display_formats.html", links = links)
    
def get_bdo_fund_values():
    url = "https://www.bdo.com.ph/content/bdounibank/en-ph/personal/Investments/daily-net-asset-value.navpuProductListing.json"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://www.bdo.com.ph/personal/Investments/daily-net-asset-value',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    response = requests.get(url, headers=headers)
    return response.json()

@bdo_bp.route("/json")
def get_bdo_fund_values_json():
    json = get_bdo_fund_values()
    return jsonify(json)

def get_bdo_fund_values_df():
    json = get_bdo_fund_values()
    df = pd.DataFrame(json["dataList"])
    return df

@bdo_bp.route("/csv")
def get_bdo_fund_values_csv():
    df = get_bdo_fund_values_df()
    csv = df.to_csv(index = False)
    return Response(csv, mimetype = "text/plain")

@bdo_bp.route("/table")
def get_bdo_fund_values_table():
    df = get_bdo_fund_values_df()
    return df.to_html(index = False)