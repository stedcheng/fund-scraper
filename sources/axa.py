from flask import Blueprint, jsonify, render_template, Response
import requests
import pandas as pd

axa_bp = Blueprint("axa", __name__, url_prefix = "/axa")

@axa_bp.route("/")
def axa_landing_page():
    links = [
        {"name": "JSON", "url": "/axa/json"},
        {"name": "CSV", "url": "/axa/csv"},
        {"name": "Table", "url": "/axa/table"}
    ]
    return render_template("display_formats.html", links = links)

def get_axa_fund_values():
    url = "https://www.axa.com.ph/bin/public/ecomm/fundtable/prices"
    response = requests.get(url)
    return response.json()

@axa_bp.route("/json")
def get_axa_fund_values_json():
    json_data = get_axa_fund_values()
    return jsonify(json_data)

axa_table_indices = ["fundName", "fundCode"]
axa_table_metrics = ["currency", "orderPrice", "bidPrice", "return1Year", "return3Year", "return5Year"]

# We won't use these for now
axa_table_indices_display = [
    ("Fund", "Name"),
    ("Fund", "Code")
]
axa_table_metrics_display = [
    ("Value", "Currency"), 
    ("Value", "Order Price"), 
    ("Value", "Bid Price"),
    ("Annualized Return", "1 Year"),
    ("Annualized Return", "3 Years"),
    ("Annualized Return", "5 Years")
]

def get_axa_fund_values_df():
    json_data = get_axa_fund_values()
    df_list = []
    for i in range(len(json_data)):
        if json_data[i]["groupName"] != "Top Five Fund":
            df_group = pd.DataFrame(json_data[i]["groupData"])
            df_group["groupName"] = json_data[i]["groupName"]
            df_list.append(df_group)

    df = pd.concat(df_list)
    df = df.drop(columns = ["fundFactSheet"])
    df = df.explode("fundData")
    df["metric"] = axa_table_metrics * len(df["fundCode"].unique())
    df = df.pivot(index = axa_table_indices, columns = "metric", values = "fundData").reset_index()
    df.columns.name = None
    df = df[axa_table_indices + axa_table_metrics]
    return df

@axa_bp.route("/csv")
def get_axa_fund_values_csv():
    df = get_axa_fund_values_df()
    csv = df.to_csv(index = False)
    return Response(csv, mimetype = "text/plain")

@axa_bp.route("/table")
def get_axa_fund_values_table():
    df = get_axa_fund_values_df()
    return df.to_html(index = False)