var express = require('express')
var websocket = require('websocket')

// basic server setup
let app = express(); 
var port = 3000;
var server = app.listen( port, serverStarted(port))

app.get('/', (req, res) => {
    res.send('Consistency Manager - happy to see you')
} )


// --- utility functions
function serverStarted(port){
    console.log(`CM server started on port ${port}`)
}