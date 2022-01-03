from server import app
from flask import render_template, jsonify, request, make_response


@app.route('/')
def render_landing_page():
    return render_template("index.html")


@app.route('/api/ReportTransaction', methods=["POST"])
def report_transaction():
    # decode request args

    bdy = request.json
    print(bdy)


    # respond with a json object
    response_json = {
        "status": "ok"
    }

    return jsonify(response_json)


