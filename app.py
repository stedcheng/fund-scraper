from flask import Flask, render_template
import os

from sources import *

app = Flask(__name__)
for bp in [axa_bp, sunlife_bp, investa_bp, bdo_bp, dragonfi_bp]:
    app.register_blueprint(bp)

@app.route("/")
def home():
    institution_fund_details = [
        {"name": "Sun Life VUL Funds", "code": "Sun Life", "url": "/sunlife"},
        {"name": "AXA VUL Funds", "code": "AXA", "url": "/axa"},
        {"name": "BDO Funds", "code": "BDO", "url": "/bdo"}
    ]

    investa_fund_details = [
        {
            "name": name,
            "code": code,
            "url": f"/investa/{code}",
            "platform": "Investa"
        } for name, code in sorted_investa_fund_names_codes.items()
    ]

    dragonfi_fund_details = [
        {
            "name": name,
            "code": code,
            "url": f"/dragonfi/{code}",
            "platform": "Dragonfi"
        } for name, code in sorted_dragonfi_fund_names_codes.items()
    ]

    inv_platforms_fund_details = sorted(
        investa_fund_details + dragonfi_fund_details, 
        key = lambda x: x["name"]
    )

    return render_template("display_funds.html", institution_fund_details = institution_fund_details, inv_platforms_fund_details = inv_platforms_fund_details)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host = "0.0.0.0", port = port, debug = True)