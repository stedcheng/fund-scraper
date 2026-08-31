from flask import Blueprint, jsonify, render_template, Response
import requests
import pandas as pd
import datetime
import json
import os
import logging
logging.basicConfig(level=logging.INFO)

sunlife_bp = Blueprint("sunlife", __name__, url_prefix = "/sunlife")

sunlife_table_columns = [
    "fundName", "fundCode", "weekly", "risk",
    "fundDate", "ingeniumDate",
    "fundCurrency", "fundVal",
    "fundYoyVal", "fundYtdVal"
]

# We won't use this for now
sunlife_table_display = [
    ("Fund", "Name"), ("Fund", "Code"), ("Fund", "Weekly"), ("Fund", "Risk"),
    ("Date", "Date"), ("Date", "Ingenium"),
    ("Value", "Currency"), ("Value", "Value"),
    ("Return", "YoY"), ("Return", "YtD")
]

@sunlife_bp.route("/")
def sunlife_landing_page():
    links = [
        {"name": "JSON", "url": "/sunlife/json"},
        {"name": "CSV", "url": "/sunlife/csv"},
        {"name": "Table", "url": "/sunlife/table"}
    ]
    return render_template("display_formats.html", links = links)
    
def get_sunlife_fund_values():
    url = "https://www.sunlife.com.ph/funds/navprice/vul/latest"
    headers = {
        'accept': 'text/plain, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,en-PH;q=0.8',
        # 'content-length': '0',
        'origin': 'https://www.sunlife.com.ph',
        'priority': 'u=1, i',
        'referer': 'https://www.sunlife.com.ph/en/insurance/vul-fund-prices/',
        'sec-ch-device-memory': '16',
        'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Microsoft Edge";v="152"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-full-version-list': '"Chromium";v="152.0.7977.65", "Not?A_Brand";v="24.0.0.0", "Microsoft Edge";v="152.0.4191.53"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36 Edg/152.0.0.0',
        'x-requested-with': 'XMLHttpRequest'
    }
    params = {
        "version": "1",
        "language": "en-us",
    }
    response = requests.post(url, params = params, headers = headers)
    print(response.text, flush = True)
    logging.info("Response text: %s", response.text[:300])
    return response.json()

@sunlife_bp.route("/json")
def get_sunlife_fund_values_json():
    json_data = get_sunlife_fund_values()
    return jsonify(json_data)

def get_sunlife_fund_values_df():
    json_data = get_sunlife_fund_values()
    df_list = []
    for i in range(len(json_data)):
        df_group = pd.DataFrame(list(json_data.values())[i])
        df_list.append(df_group)

    df = pd.concat(df_list)
    df.drop(columns = ["readFlag", "status", "fundDesc"])
    df.columns.name = None
    df = df[sunlife_table_columns]
    return df

@sunlife_bp.route("/csv")
def get_sunlife_fund_values_csv():
    df = get_sunlife_fund_values_df()
    csv = df.to_csv(index = False)
    return Response(csv, mimetype = "text/plain")

@sunlife_bp.route("/table")
def get_sunlife_fund_values_table():
    df = get_sunlife_fund_values_df()
    return df.to_html(index = False)