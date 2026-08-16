from flask import Blueprint, jsonify, render_template, Response
import requests
import pandas as pd
import datetime
import pytz

dragonfi_bp = Blueprint("dragonfi", __name__, url_prefix = "/dragonfi")

# Source:
# resp = requests.get("https://api.dragonfi.ph/api/v2/Fund/GetFundPagedList?Asc=true&SortBy=fundName&PageNum=1&PageSize=100")
# pd.DataFrame(resp.json()["fundList"]).sort_values("fundId").to_csv("dragonfi_funds.csv")
df_fund_codes = pd.read_csv("sources/dragonfi_funds.csv")
sorted_dragonfi_fund_names_codes = {
    df_fund_codes["fundName"].iloc[i]: df_fund_codes["fundCode"].iloc[i] 
    for i in range(len(df_fund_codes))
}

@dragonfi_bp.route("/<fund_code>/")
def dragonfi_landing_page(fund_code):
    links = [
        {"name": "JSON", "url": f"/dragonfi/{fund_code}/json"},
        {"name": "CSV", "url": f"/dragonfi/{fund_code}/csv"},
        {"name": "Table", "url": f"/dragonfi/{fund_code}/table"}
    ]
    return render_template("display_formats.html", links = links)
    
def get_dragonfi_fund_values(fund_code):
    url = f"https://api.dragonfi.ph/api/v2/Fund/GetFundNAVPU?fundCode={fund_code}&dateRange=All"
    response = requests.get(url)
    return response.json()

@dragonfi_bp.route("/<fund_code>/json")
def get_dragonfi_fund_values_json(fund_code):
    json_data = get_dragonfi_fund_values(fund_code)
    return jsonify(json_data)

def get_dragonfi_fund_values_df(fund_code):
    json_data = get_dragonfi_fund_values(fund_code)
    df = pd.DataFrame(json_data["fundNAVPUList"])
    for col in ["date", "dateEntry"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    return df

@dragonfi_bp.route("/<fund_code>/csv")
def get_dragonfi_fund_values_csv(fund_code):
    df = get_dragonfi_fund_values_df(fund_code)
    csv = df.to_csv(index = False)
    return Response(csv, mimetype = "text/plain")

@dragonfi_bp.route("/<fund_code>/table")
def get_dragonfi_fund_values_table(fund_code):
    df = get_dragonfi_fund_values_df(fund_code)
    return df.to_html(index = False)

resp = requests.get("https://api.dragonfi.ph/api/v2/Fund/GetFundNAVPU?fundCode=BS4&dateRange=All")
pd.DataFrame(resp.json()["fundNAVPUList"])