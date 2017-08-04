
exports.$unregisterOperationId = function(args, res, next) {
  /**
   * parameters expected in the args:
  * $apiName ($pascalName)
  **/
    var examples = {};
  examples['application/json'] = {
  "query" : "aeiou",
  "callback" : "aeiou",
  "id" : "aeiou"
};
  if(Object.keys(examples).length > 0) {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(examples[Object.keys(examples)[0]] || {}, null, 2));
  }
  else {
    res.end();
  }

}
