

exports.$retrieveOperationId = function (req, res, next) {
    /**
     * parameters expected in the args:
     * $apiId (String)
     * fields (String)
     **/

    var args = req.swagger.params;

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
        var $apiId = String(req.swagger.params.$apiId.value);

        const query = {
            id: $apiId
        }


        collection.findOne(query, function (err, doc) {


            try {
            assert.equal(err, null);
            }
            catch (err) {

            console.log(err);

            res.statusCode = 500;
            var error = { };
            error = { 'code': 'ERR0001' , 'reason' : err , 'message:' : 'provide a different id' };
            res.end(JSON.stringify(error));
             }

            if (doc == null) {
                res.statusCode = 404;
                var error = {
                };
                error = {
                    'code':   'ERR0001', 'reason': 'not found', 'message:': 'provide a different id'
                };
                res.end(JSON.stringify(error));
            } else {
                res.setHeader('Content-Type', 'application/json');
                delete doc[ "_id"]

                res.end(JSON.stringify(doc));
            }
        })
    })
}

