

exports.$updateOperationId = function (req, res, next) {

    var args = req.swagger.params;
    /**
     * parameters expected in the args:
     * $apiId (String)
     * $apiName ($pascalName)
     **/


     MongoClient.connect(credentials.uri, {
             mongos: {
                 ssl: true,
                 sslValidate: true,
                 sslCA: ca,
                 poolSize: 1,
                 reconnectTries: 1
             }
         },
         function(err, db) {
        assert.equal(null, err);
        var collection = mongodb.collection('$apiName');

        var $apiName = req.swagger.params.$apiName.value;
        var $apiId = String(req.swagger.params.$apiId.value);



        const query = {
            id: $apiId
        }

        var patchDoc = {
            $set: $apiName
        }

        collection.update(query, patchDoc, function (err, doc) {
            assert.equal(err, null);
            //res.json(doc);
            // Find one document
            collection.findOne(query, function (err, doc) {
                res.setHeader('Content-Type', 'application/json');
                delete doc[ "_id"]
                res.end(JSON.stringify(doc));
            })
        })
    })
}

