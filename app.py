from flask import Flask, render_template
import os

from sources import *

app = Flask(__name__)
app.register_blueprint(axa_bp)
app.register_blueprint(sunlife_bp)
app.register_blueprint(investa_bp)

investa_fund_codes = ["PHMF:MTPHMM1", "PHMF:ALFMMFU"]

@app.route("/")
def home():
    links = [
        {"name": "Sun Life", "url": "/sunlife"},
        {"name": "AXA", "url": "/axa"},
    ]

    # Add one link per fund code
    for code in investa_fund_codes:
        links.append({
            "name": f"{code} via Investa",
            "url": f"/investa/{code}"
        })
    return render_template("display_links.html", links = links)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host = "0.0.0.0", port = port, debug = True)