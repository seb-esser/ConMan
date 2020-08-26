var express = require('express')
var router = express.Router();

// custom modules
var updateTypes = require('../enums/enum-updateTypes')

// // middle ware
// router.use(function timeLog(req, res, next) {
//     console.log('Called Middleware commonEnums');
//     next();
// });

router.get('/getUpdateTypes', (req, res) => {
    res.send(updateTypes);
})

module.exports = router;