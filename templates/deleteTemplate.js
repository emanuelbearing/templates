
//TODO check this functionality offline before!!!!
exports.$deleteOperationId = function (req, res, next) {

    var args = req.swagger.params;
    /**
     * parameters expected in the args:
     * $apiId (String)
     * $apiName ($pascalName)
     **/

    var $apiId = String(req.swagger.params.$apiId.value);

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
      if (err) throw err;
      var query = {
        id: $apiId
      };

      mongodb.collection('$apiName').deleteOne(query, function(err, obj) {
        if (err) throw err;

        res.setHeader('Content-Type', 'application/json');

        if (obj.result.n == 1){
            res.statusCode = 204;
            res.end(JSON.stringify(obj));
        }

        if (obj.result.n == 0){
            error = {
                'code':   'ERR0001', 'message': 'Entry not found', 'description': 'provide a different id' , 'infoURL': '-'
            };
            res.statusCode = 404;
            res.end(JSON.stringify(error));
        }

        //db.close();

        });
    });
}
