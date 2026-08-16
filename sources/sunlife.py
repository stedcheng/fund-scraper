from flask import Blueprint, jsonify, render_template, Response
import requests
import pandas as pd
import datetime
import json
import os

sunlife_bp = Blueprint("sunlife", __name__, url_prefix = "/sunlife")
cache = {}

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

def save_cache_to_file():
    with open("cache/sunlife.json", "w") as f:
        json.dump(cache["sunlife"], f)

def load_cache_from_file():
    if os.path.exists("cache/sunlife.json"):
        with open("cache/sunlife.json") as f:
            cache["sunlife"] = json.load(f)

load_cache_from_file()

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
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0",
    }
    params = {
        "version": "1",
        "language": "en-us",
    }
    response = requests.post(url, params=params, headers=headers)
    try:
        data = response.json()
        cache["sunlife"] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "data": data,
        }
        save_cache_to_file()
    except ValueError:
        data = None
        status_code = response.status_code
        body = response.text[:500]
        error_dict = {
            "data": data, "status_code": status_code, "body": body
        }
        return error_dict

@sunlife_bp.route("/json")
def get_sunlife_fund_values_json():
    if "sunlife" not in cache:
        get_sunlife_fund_values()
        return jsonify(cache["sunlife"])
    else:
        ts = cache["sunlife"]["timestamp"]
        cache_date = datetime.datetime.fromisoformat(ts).date()
        today = datetime.date.today()
        if cache_date == today:
            return jsonify(cache["sunlife"])
        else:
            get_sunlife_fund_values()
            return jsonify(cache["sunlife"])

def get_sunlife_fund_values_df():
    if "sunlife" not in cache:
        get_sunlife_fund_values()
    json_data = cache["sunlife"]["data"]
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