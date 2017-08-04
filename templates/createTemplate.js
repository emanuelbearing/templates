

exports.$createOperationId = function (req, res, next) {
    /**
     * parameters expected in the args:
     * $apiName ($pascalName)
     **/
    var args = req.swagger.params;

    var $apiName = args.$apiName.value;

    if ($apiName.id == undefined) {
        $apiName.id = uuid.v4();
    }



    var self = req.url + "/" + $apiName.id;


    $apiName.href = req.headers.origin + self;

    // Use connect method to connect to the server
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
            if (err) {
                console.log("Create $pascalName"+err);
            } else {
              assert.equal(null, err);

              // Get the documents collection
              var collection = mongodb.collection('$apiName');
              // Insert some documents
              collection.insert($apiName, function (err, result) {
                  assert.equal(err, null)
              });
              db.close();
            }
        }
    );



    res.setHeader('Content-Type', 'application/json');

    res.setHeader('Location', self);
    res.end(JSON.stringify($apiName));


}
