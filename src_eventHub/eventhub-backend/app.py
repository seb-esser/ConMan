import os

import jsonpickle
from flask import Flask, request, jsonify, render_template, json
from flask_cors import CORS, cross_origin
from flask_socketio import send, emit, SocketIO

from werkzeug.exceptions import HTTPException

from data_structures.ModelData import ModelData
from data_structures.SubscriptionManagement.SubscriptionModel import SubscriptionModel
from data_structures.Teams.DeliveryTeam import DeliveryTeam
from data_structures.Teams.Member import Member
from functions.neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from functions.neo4j_middleware.neo4jConnector import Neo4jConnector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resource={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

topic_hierarchy = {
    "architectureModel":
        {
            "components": [
                "Wall",
                "Column",
                "Beam",
                "Slab",
                "Window",
                "Door",
                "Voiding"
            ]},
    "structuralModel":
        {
            "components": [
                "Wall",
                "Column",
                "Beam",
                "Slab",
                "Foundation"]
        },
    "HvacModel":
        {
            "components": [
                "Pipe",
                "Duct"
            ]
        }
}


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


@app.route('/api/getModels', methods=['GET'])
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

        # beautify timestamp
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


@app.route('/api/getDeliveryTeams', methods=['GET'])
def get_delivery_teams():
    teams = DeliveryTeam.from_db()
    return app.response_class(
        status=200,
        response=jsonpickle.dumps(teams, unpicklable=False),
        mimetype='application/json'
    )


@app.route('/api/CreateDeliveryTeam', methods=['POST'])
def create_delivery_team():
    name = eval(request.data)["teamName"]
    team = DeliveryTeam(name=name)

    # send to db and get back the primary key val
    team.to_db()
    
    team.id = team.get_team_by_id(team.uuid)

    return app.response_class(
        status=200,
        response=jsonpickle.dumps(team, unpicklable=False),
        mimetype='application/json'
    )


@app.route('/api/deleteDeliveryTeam', methods=["DELETE"])
def delete_delivery_team():
    uuid = eval(request.data)['uuid']
    team = DeliveryTeam.from_db_by_uuid(uuid)

    team.delete_team(uuid)

    # make response
    return app.response_class(
        status=200
    )


@app.route('/api/getMembers', methods=['GET'])
def get_members():
    members = Member.from_db()
    return app.response_class(
        status=200,
        response=jsonpickle.dumps(members, unpicklable=False),
        mimetype='application/json'
    )


@app.route('/api/createMember', methods=['POST'])
def create_member():
    # cast incoming byte array to dict
    data = eval(request.data)

    # instantiate member instance
    member = Member(last_name=data["LastName"], first_name=data["FirstName"], team_id=data["TeamId"])
    # send it to db
    member.to_db()

    # make response
    return app.response_class(
        status=200,
        response=jsonpickle.dumps(member, unpicklable=False),
        mimetype='application/json'
    )


@app.route('/api/deleteMember', methods=["DELETE"])
def delete_member():
    uuid = eval(request.data)['uuid']
    member = Member.from_db_by_uuid(uuid)

    # remove member from table
    member.delete_member(uuid)

    # make response
    return app.response_class(
        status=200
    )


@app.route('/api/getSubscriptionModelIds')
def get_subscription_model_ids():

    response = {"SubscriptionModels": []}

    # specify the path where the JSONs are stored inside the server
    model_path = "data_structures/SubscriptionManagement/models"
    for file in os.listdir(model_path):
        if file.startswith("SubscriptionModel_"):
            model: SubscriptionModel = SubscriptionModel.from_json(path=model_path + "/" + file)
            response["SubscriptionModels"].append({"modelUUID": model.uuid, "modelName": model.name})
    # make response
    return app.response_class(
        status=200,
        response=jsonpickle.dumps(response, unpicklable=False),
        mimetype='application/json'
    )


@app.route('/api/getSubscriptionModel', methods=["GET"])
def get_subscription_model():
    model_id = eval(request.data)['modelUUID']

    # specify the path where the JSONs are stored inside the server
    model_path = "data_structures/SubscriptionManagement/models"
    for file in os.listdir(model_path):
        if file.startswith("SubscriptionModel_"):
            model: SubscriptionModel = SubscriptionModel.from_json(path=model_path + "/" + file)
            if model.uuid == model_id:

                # make response
                return app.response_class(
                    status=200,
                    response=jsonpickle.dumps(model, unpicklable=False),
                    mimetype='application/json'
                )

    # if no model was found under the requested id, make 404 response
    return app.response_class(
        status=404
    )


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
    print("[WS]\t SID: {}".format(request.sid))


@socketio.event()
def connect():
    print("[WS]: New client has connected via websocket on default namespace.")
    print("[WS]\t SID: {} ".format(request.sid))


@socketio.event(namespace="/websocketTest")
def disconnect():
    print("[WS]: Existing client has disconnected via websocket. ")
    print("[WS]\t SID: {} ".format(request.sid))


@socketio.event
def disconnect():
    print("[WS]: Existing client has disconnected via websocket. ")
    print("[WS]\t SID: {}".format(request.sid))


if __name__ == '__main__':
    print("Starting server ... ")
    socketio.run(app)

# https://stackoverflow.com/questions/68383027/how-to-integrate-python-socket-io-with-qt
