from flask import Flask, render_template
import os

from sources import *

app = Flask(__name__)
app.register_blueprint(axa_bp)
app.register_blueprint(sunlife_bp)
app.register_blueprint(investa_bp)

@app.route("/")
def home():
    fund_details = [
        {"name": "Sun Life VUL Funds", "code": "Sun Life", "url": "/sunlife"},
        {"name": "AXA VUL Funds", "code": "AXA", "url": "/axa"},
    ]

    # Add one link per fund code
    for name, code in sorted_investa_fund_names_codes.items():
        fund_details.append({
            "name": f"{name} (via Investa)",
            "code": code,
            "url": f"/investa/{code}"
        })
    return render_template("display_funds.html", fund_details = fund_details)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host = "0.0.0.0", port = port, debug = True)