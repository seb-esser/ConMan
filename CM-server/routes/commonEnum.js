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

// router.post('/addUpdateType', addUpdateType(req, res) );

// function addUpdateType(req, res) {
//     var num = updateTypes.length + 1;
//     var newUpdateType = { asdf, num }
//     updateTypes.push(newUpdateType)
//     return updateTypes;
// }



router.post('/addUpdateType', (req, res) => {
    var newType = req.body.updateType;
    console.log(`Adding new update type: -- ${newType} --. Processing...`);

    const updateType = {
        name: req.params["name"],
        id: updateTypes.length + 1
    }
    updateTypes.push(updateType);

    res.send(updateTypes);

});


module.exports = router;