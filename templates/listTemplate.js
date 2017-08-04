

exports.$listOperationId = function (req, res, next) {
    /**
     * parameters expected in the args:
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
          try {
            assert.equal(null, err);
        }
        catch (err) {
            console.log("Find "+err)
        }




        // Get the documents collection and filtering ?

        var collection = mongodb.collection('$apiName');



        // console.log(req)

        console.log(req.query);


        var queryToMongo = require('query-to-mongo')
        var query = queryToMongo(req.query)
        console.log(query)

        // Find some documents based on criteria plus attribute selection
        collection.find(query.criteria,
        mongoUtils.fieldFilter(args.fields.value)).toArray(function (err, docs) {
            assert.equal(err, null);
            console.log(docs);
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify(docs));
            //res.json( docs );
        });


    })
}


