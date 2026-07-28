from flask import Flask, jsonify, render_template, Response
import requests
import os
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    links = [
        {"name": "Sun Life", "url": "/sunlife"},
        {"name": "AXA", "url": "/axa"}
    ]
    return render_template("display_links.html", links = links)

@app.route("/axa")
def axa_landing_page():
    links = [
        {"name": "JSON", "url": "/axa/json"},
        {"name": "CSV", "url": "/axa/csv"},
        {"name": "Table", "url": "/axa/table"}
    ]
    return render_template("display_links.html", links = links)

def get_axa_fund_values():
    url = "https://www.axa.com.ph/bin/public/ecomm/fundtable/prices"
    response = requests.get(url)
    return response.json()

@app.route("/axa/json")
def get_axa_fund_values_json():
    json = get_axa_fund_values()
    return jsonify(json)

axa_table_indices = ["fundName", "fundCode"]
axa_table_metrics = ["currency", "orderPrice", "bidPrice", "return1Year", "return3Year", "return5Year"]

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

sunlife_table_columns = [
    "fundName", "fundCode", "weekly", "risk",
    "fundDate", "ingeniumDate",
    "fundCurrency", "fundVal",
    "fundYoyVal", "fundYtdVal"
]

sunlife_table_display = [
    ("Fund", "Name"), ("Fund", "Code"), ("Fund", "Weekly"), ("Fund", "Risk"),
    ("Date", "Date"), ("Date", "Ingenium"),
    ("Value", "Currency"), ("Value", "Value"),
    ("Return", "YoY"), ("Return", "YtD")
]

def get_axa_fund_values_df():
    json = get_axa_fund_values()
    df_list = []
    for i in range(len(json)):
        if json[i]["groupName"] != "Top Five Fund":
            df_group = pd.DataFrame(json[i]["groupData"])
            df_group["groupName"] = json[i]["groupName"]
            df_list.append(df_group)

    df = pd.concat(df_list)
    df = df.drop(columns = ["fundFactSheet"])
    df = df.explode("fundData")
    df["metric"] = axa_table_metrics * len(df["fundCode"].unique())
    df = df.pivot(index = axa_table_indices, columns = "metric", values = "fundData").reset_index()
    df.columns.name = None
    df = df[axa_table_indices + axa_table_metrics]
    return df

@app.route("/axa/csv")
def get_axa_fund_values_csv():
    df = get_axa_fund_values_df()
    csv = df.to_csv(index = False)
    return Response(csv, mimetype = "text/plain")

@app.route("/axa/table")
def get_axa_fund_values_table():
    df = get_axa_fund_values_df()
    df.columns = pd.MultiIndex.from_tuples(axa_table_indices_display + axa_table_metrics_display)
    return df.to_html(index = False)

@app.route("/sunlife")
def sunlife_landing_page():
    links = [
        {"name": "JSON", "url": "/sunlife/json"},
        {"name": "CSV", "url": "/sunlife/csv"},
        {"name": "Table", "url": "/sunlife/table"}
    ]
    return render_template("display_links.html", links = links)
    
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
    return response.json()

@app.route("/sunlife/json")
def get_sunlife_fund_values_json():
    json = get_sunlife_fund_values()
    return jsonify(json)

def get_sunlife_fund_values_df():
    json = get_sunlife_fund_values()
    df_list = []
    for i in range(len(json)):
        df_group = pd.DataFrame(list(json.values())[i])
        df_list.append(df_group)

    df = pd.concat(df_list)
    df.drop(columns = ["readFlag", "status", "fundDesc"])
    df.columns.name = None
    df = df[sunlife_table_columns]
    return df

@app.route("/sunlife/csv")
def get_sunlife_fund_values_csv():
    df = get_sunlife_fund_values_df()
    csv = df.to_csv(index = False)
    return Response(csv, mimetype = "text/plain")

@app.route("/sunlife/table")
def get_sunlife_fund_values_table():
    df = get_sunlife_fund_values_df()
    df.columns = pd.MultiIndex.from_tuples(sunlife_table_display)
    return df.to_html(index = False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)