from flask import Blueprint, jsonify, render_template, Response
import requests
import pandas as pd
import datetime
import pytz

investa_bp = Blueprint("investa", __name__, url_prefix = "/investa")

@investa_bp.route("/<fund_code>/")
def investa_landing_page(fund_code):
    links = [
        {"name": "JSON", "url": f"/investa/{fund_code}/json"},
        {"name": "CSV", "url": f"/investa/{fund_code}/csv"},
        {"name": "Table", "url": f"/investa/{fund_code}/table"}
    ]
    return render_template("display_links.html", links = links)
    
def get_investa_fund_values(fund_code):
    # fund_code = "PHMF:MTPHMM1"
    # fund_code = "PHMF:ALFMMFU"
    url = f"https://webapi.investagrams.com/InvestaApi/TradingViewChart/history?symbol={fund_code}&resolution=1D&from=0&to=2000000000&countBack=100000"
    headers = {
        "Referer": "https://www.investagrams.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0",
    }
    response = requests.get(url, headers=headers)
    return response.json()

@investa_bp.route("/<fund_code>/json")
def get_investa_fund_values_json(fund_code):
    json = get_investa_fund_values(fund_code)
    return jsonify(json)

def get_investa_fund_values_df(fund_code):
    json = get_investa_fund_values(fund_code)
    df = pd.DataFrame({
        k: v for k, v in json.items() if isinstance(v, list)
    })
    df["t_2"] = df["t"].apply(lambda ts: datetime.datetime.fromtimestamp(ts, tz = pytz.timezone("UTC")).strftime("%Y-%m-%d"))
    return df

@investa_bp.route("/<fund_code>/csv")
def get_investa_fund_values_csv(fund_code):
    df = get_investa_fund_values_df(fund_code)
    csv = df.to_csv(index = False)
    return Response(csv, mimetype = "text/plain")

@investa_bp.route("/<fund_code>/table")
def get_investa_fund_values_table(fund_code):
    df = get_investa_fund_values_df(fund_code)
    return df.to_html(index = False)