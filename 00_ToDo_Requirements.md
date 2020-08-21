## Required functions of @server.js
- Enum of update types, which the clients can query
- Enum of involved domains, which the clients can use to address specific updates

- Socket connector and disconnector
- Logging-functions (check incoming updates)
- History of incoming updates incl. timestamp -> enable disconnected clients to get all updates eventually
- MessageToReceiver -> define receivers that must consume incoming updates (idea of blacklist and whitelist)

-> nodeJs based
-> implements webSocket

## Required functions for @client.py
- ComputeDiff(initial, updated)
- FormulatePatch()
    - use the GET domains and GET updateTypes functions from the main server!
- connectSocket()
- disconnectSocket()
- emitUpdate()
- OnUpdateAvailableWhileConnected()
- GetAllUpdatesAfterDisconnection()

-> use interactive command lines
-> implements webSocket

All other clients have to implement the same reference architecture for their clients as the python-based approach does



