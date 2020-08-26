// --- import packages ---
var express = require('express')
var websocket = require('websocket')


// custom modules

// --- code ---

// basic server setup
let app = express();
var port = process.env.PORT || 3000; // use the env defined port or define individual port
var server = app.listen(port, serverStarted(port))

// ensure correct encoding of json-based post requests

// Parse JSON bodies (as sent by API clients)
app.use(express.json());


// routing the landing page
app.get('/', (req, res) => {
    var ip = req.connection.remoteAddress || req.headers['x-forwarded-for'];
    console.log(`${ip} has requested the landing page.`)
    res.sendFile('public/index.html', { root: __dirname });
});

// import all routes of the server
var commonEnums = require('./routes/commonEnum');
app.use('/api', commonEnums);



// --- utility functions ---
function serverStarted(port) {
    console.log(`CM server started on port ${port}`)
}