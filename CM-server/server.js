// --- import packages ---
var express = require('express');
var socket = require('socket.io');
var morgan = require('morgan')
var fs = require('fs')
var path = require('path')

// custom modules

// --- code ---

// basic server setup
let app = express();
var port = process.env.PORT || 3000; // use the env defined port or define individual port
var server = app.listen(port, serverStarted(port))

// ensure correct encoding of json-based post requests - Parse JSON bodies (as sent by API clients)
app.use(express.json());

// register morgan logger
// create a write stream (in append mode)
var accessLogStream = fs.createWriteStream(path.join(__dirname, 'access.log'), { flags: 'a' })
app.use(morgan('common', { stream: accessLogStream }));


// routing the landing page
app.get('/', (req, res) => {
    var ip = req.connection.remoteAddress || req.headers['x-forwarded-for'];
    console.log(`${ip} has requested the landing page.`)
    res.sendFile('public/index.html', { root: __dirname });
});

// routing the admin page
app.get('/admin/', (req, res) => {
    var ip = req.connection.remoteAddress || req.headers['x-forwarded-for'];
    console.log(`${ip} has requested the admin panel.`)
    res.sendFile('public/admin.html', { root: __dirname });
});

// import all REST routes of the server
var commonEnums = require('./routes/commonEnum');
app.use('/api', commonEnums);

// --- Socket setup
var io = socket(server);
io.on('connection', (socket) => {
    console.log(`made socket connection: \t ${socket.id}`);

    socket.on('disconnect', () => {
            console.log(`user disconnected:\t \t ${socket.id} `)
        })
        // Handle chat event
    socket.on('updatePatch', function(data) {
        console.log(data);
        io.sockets.emit('updatePatchConfirm', 'thank you');
        socket.broadcast.emit('updatePatchConfirm', data);
    });

    // // Handle typing event
    // socket.on('typing', function(data){
    //     socket.broadcast.emit('typing', data);
});

// --- utility functions ---
function serverStarted(port) {
    console.log(`CM server started on port ${port}`)
        // logger.info(`Server started on ${port}`)
}