from server import app
from flask import render_template, jsonify, request


@app.route('/')
def render_landing_page():
    return render_template("index.html")


@app.route('/api/stations/', methods=["GET"])
def get_station_by_name():
    # decode request args
    args = request.args.get('station')

    # respond with a json object
    return ""

