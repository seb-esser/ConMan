var express = require('express')
var websocket = require('websocket')

// custom modules
var updateTypes = require('./enums/enum-updateTypes')

// basic server setup
let app = express();
var port = 3000;
var server = app.listen(port, serverStarted(port))

// routing the landing page
app.get('/', (req, res) => {
    var ip = req.connection.remoteAddress || req.headers['x-forwarded-for'];
    console.log(`${ip} has requested the landing page.`)
    console.log(updateTypes);
    res.sendFile('public/index.html', { root: __dirname });
});

// import all routes of the server
var commonEnums = require('./routes/commonEnum');
app.use(commonEnums);

// --- utility functions
function serverStarted(port) {
    console.log(`CM server started on port ${port}`)
}