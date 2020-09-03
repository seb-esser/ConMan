
# --- imports ---
from flask import Flask, request
import socketio
import os
import ifcopenshell
from neo4jConnector import Neo4jConnector 

# - define some basic objects
app = Flask(__name__)
app.config['DEBUG'] = False

sio = socketio.Client()

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# -- http routes
@app.route('/')
def hello():    
    # frontend message
    return "Hello World!"

@app.route('/emit-test')
def emitTest(): 
    sio.emit('updatePatch', 'This is my first websocket-based message ever. Celebrate this!')
    return "test the emit function"

@app.route('/loadIfcJSON', methods=['POST'])
def map_to_neo4j(): 

    print('parsing json from post request body...') 
    ifc_json = request.get_json()

    if ifc_json == None:
        return 'empty request body. please check. '

    print('connecting to neo4j database... ')
    connector = Neo4jConnector()
    connector.connect_driver()
    
    try:
         for entity in ifc_json['data']:
            cypher_statement = 'Create(n:' + entity['type'] + "{globalId: " + '"{}"'.format(entity['globalId']) + '})'
            print(cypher_statement)
            connector.run_cypher_statement(cypher_statement)
                          
#for attr, val in entity.items():
            #    if isinstance(val, dict) or isinstance(val, list):
            #        # dealing with lists and arrays
            #        prop_val = hash(str(val))
            #    else:
            #        # dealing with a atomic property
            #        prop_val = val
            
            #    print('\t{:<25}: {}'.format(attr, prop_val))
            print('\n')

    except :
        pass
   
    connector.disconnect_driver()       


    # print(data)
    return "successful"

@app.route('/getIfcJSON')
def getJson():
    return ifc_json

# --- catch socket events :
#   syntax pattern:
#       def <socketHeader>(<socketData>):
#           ...  do something ...
# ---
@sio.event
def connect():
    print('#Socket-Event: \t connected to server')

@sio.event
def updatePatchConfirm(data):
    print('message received:\n \t ', data)

@sio.event
def disconnect():
    print('#Socket-Event: \t disconnected from server')


# --- main function ---
if __name__ == '__main__':
    
    HOST = os.environ.get('SERVER_HOST', 'localhost')

    #try:
    #    PORT = int(os.environ.get('SERVER_PORT', '5000'))
    #except ValueError:
    #    PORT = 5000

    # connect socket
    print('trying to connect socket to CM server...')
    # sio.connect('http://localhost:3000')
    print('connected to CM server as {}'.format(sio.sid))

    app.run(port=4000, threaded=True)


