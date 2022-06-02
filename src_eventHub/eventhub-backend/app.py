import jsonpickle
from flask import Flask, request, jsonify, render_template, json
from flask_cors import CORS, cross_origin
from flask_socketio import send, emit, SocketIO

from werkzeug.exceptions import HTTPException

from data_structures.ModelData import ModelData
from functions.neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from functions.neo4j_middleware.neo4jConnector import Neo4jConnector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resource={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.route('/api/getModels')
def get_models():
    cy = Neo4jQueryFactory.get_loaded_models()
    connector = Neo4jConnector()
    connector.connect_driver()
    raw = connector.run_cypher_statement(cy)
    connector.disconnect_driver()

    i = 0
    all_models = []
    for record in raw:

        model_name = record[0]
        timestamp = [x for x in record[1] if x.startswith("ts")][0]

        #beautify timestamp
        ts = "{}-{}-{}_{}-{}-{}".format(timestamp[2:6], timestamp[6:8], timestamp[8:10],
                                        timestamp[11:13], timestamp[13:15], timestamp[15:17])

        if model_name not in [x.Name for x in all_models]:
            model = ModelData(model_name)
            model.set_timestamps(ts)
            all_models.append(model)

        else:
            m = [x for x in all_models if x.Name == model_name][0]
            m.timestamps.append(ts)

        i += 1

    # bundle data
    s = jsonpickle.dumps({"models": all_models}, unpicklable=False)
    # prepare response
    response = app.response_class(
        response=s,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/api/getSubscriptionHierarchy')
def get_subscription_hierarchy():
    return jsonify({"hierarchy": {"models": ["A", "B", "C"]}})


@app.route('/api/testSocket')
def test_socket():
    socketio.emit("UserConnected", "User1")
    print("triggered socket event. Emitting (\"UserConnected, User1\") ")
    response = app.response_class(
        response="success",
        status=200
    )
    return response


@socketio.event(namespace='/websocketTest')
def connect():
    print("[WS]: New client has connected via websocket on namespace websocketTest.")


@socketio.event()
def connect():
    print("[WS]: New client has connected via websocket on default namespace.")


@socketio.event(namespace="/websocketTest")
def disconnect():
    print("[WS]: Existing client has disconnected via websocket. ")


@socketio.event
def disconnect():
    print("[WS]: Existing client has disconnected via websocket. ")


if __name__ == '__main__':
    print("Starting server ... ")
    socketio.run(app)
