from string import Template
import os, errno
import yaml
import json
import fileinput

#DEFINE THIS VARIABLES
applicationName = ""
nameHost = ""

##------------------------------------------------------------------------------
#
#
def substituteVariables(filePath, dictionary):
    #open the file
    filein = open( filePath )
    #read it
    src = Template( filein.read() )
    #document data
    result = src.substitute(dictionary)
    filein.close()
    return result

##------------------------------------------------------------------------------
#
#
def createManifest(name, host):
    dictionary = { 'apiManagement':name, 'host':host }

    manifest = substituteVariables("templates/manifestTemplate.yml", dictionary)
    if manifest is not None:
        manifestFile = open("manifest.yml", 'w+')
        manifestFile.write(manifest)
        manifestFile.close()
    else:
        print("An Error occured while changing variables in manifestTemplate.yml")

def subversionExtender(version):
    subversions = len(version.split("."))
    if subversions <= 2:
        version = version + ".0" * (3 - subversions)
    return version

def editPackage():
    templateFile = open('templates/packageTemplate.json', 'r')
    templateJSON = json.load(templateFile)
    templateFile.close()
    with open('package.json', 'r+') as f:
        packageJSON = json.load(f)
        #all npm dependencies needed for swagger, mongo, bluemix etc. are given in the template
        # copy the dependencies from the template to the package.json file
        packageJSON['dependencies'] = templateJSON['dependencies']

        #NPM only accepts Versions like 2.0.0 with two subversions for starting the server
        # the following code ensures that a version has at least two suversion digits
        packageJSON['version'] = subversionExtender(packageJSON['version'])
        f.seek(0)
        f.write(json.dumps(packageJSON, sort_keys=False, indent=4))
        f.truncate()

def changeParameters(fileNames):
    #change in each Api.js file (for example TroubleTicket.js)
    for fileName in fileNames:
        file = fileinput.FileInput('controllers/'+fileName+'.js', inplace=True)
        for line in file:
            # Note this is python 2.X notation
            print line.replace("req.swagger.params", "req"),
            # When using python 3.x use the end='' keyword
        file.close()
    return 0

################################################################################
#### The following Functions are used to write the template code to the
#### Service files
################################################################################

##------------------------------------------------------------------------------
# createHeader writes the the properties for connecting with the mongoDB
# in each servicefile the first time it is called
def createHeader(pascalName):
    outputFileName = pascalName+"Service.js"
    serviceFile = open("controllers/"+outputFileName, 'w')
    template = open("templates/headerTemplate.js",'r')
    serviceFile.write(template.read())
    template.close()
    serviceFile.close()
    return 0

def extractId(lastElement):
    #check if brackets can be found in the string
    idStart = lastElement.find("{")
    idStop = lastElement.find("}")

    #if no brackets are found idStart and Stop are -1
    # 0 is returned to show that there is no id in the link
    if idStart == -1 or idStop == -1:
        return 0

    return lastElement[idStart+1:idStop]


def createApiServices(yamlDoc):
    # existingFiles hold the name of all filenames. This is used to make sure
    # that the header is only written once to each file
    existingFiles = []
    for link in yamlDoc['paths']:
        #the link has the form of /dummy, /dummy/{Id}, /hub or /hub{Id}
        #differentiate if {Id} exists
        linkSplitted = link.split("/")
        apiName = linkSplitted[1]

        # check if the last part of the link is some kind of Id following the structure {*id*}
        # if this part isn't an id 0 is returned
        id = extractId(linkSplitted[-1])

        #in each link entry we can find rest operations
        for operation in yamlDoc['paths'][link]:
            subFile = ""
            dictionary = {}

            tags = " ".join(yamlDoc['paths'][link][operation]['tags'])
            #The changes the lower to upper camelcase from dummyDummy to dummyDummy
            #This is needed for creating the automated function calles and for
            #editing the correct js files later on.
            #Hubs may have the Tag "events subscription", this function makes an
            #upper case for the first letter of each word in the list which
            #result in EventsSubscription
            # tags.split() splits up the tags, one entry for each word
            # the for loop changes the first letter x[0] to upper case
            # "".join() joins the resulting words to one string again
            pascalApi = "".join([x[0].upper()+x[1:] for x in tags.split()])


            if pascalApi not in existingFiles:
                createHeader(pascalApi)
                existingFiles.append(pascalApi)


            operationId = str(yamlDoc['paths'][link][operation]['operationId'])


            if operation == "get":
                if id != 0:
                    dictionary = { 'retrieveOperationId':operationId, 'apiName':apiName, 'apiId': id }
                    subFile = "retrieveTemplate.js"
                else:
                    dictionary = {'listOperationId': operationId, 'apiName': apiName}
                    subFile = "listTemplate.js"

            elif operation == "post":
                if apiName == "hub":
                    dictionary = { 'registerOperationId':operationId, 'apiName':apiName, 'pascalName':pascalApi }
                    subFile = "registerTemplate.js"
                else:
                    dictionary = { 'createOperationId':operationId, 'apiName':apiName, 'pascalName':pascalApi }
                    subFile = "createTemplate.js"

            elif operation == "delete":
                if apiName == "hub":
                    dictionary = { 'unregisterOperationId':operationId, 'apiName':apiName, 'pascalName':pascalApi }
                    subFile = "unregisterTemplate.js"
                else:
                    dictionary = {'deleteOperationId': operationId, 'apiName': apiName, 'pascalName': pascalApi,
                                  'apiId': id}
                    subFile = "deleteTemplate.js"

            elif operation == "patch":
                dictionary = {'patchOperationId': operationId, 'apiName': apiName, 'pascalName': pascalApi, 'apiId': id, 'set': "$set"}
                subFile = "patchTemplate.js"

            elif operation == "put":
                dictionary = {'updateOperationId': operationId, 'apiName': apiName, 'pascalName': pascalApi, 'apiId': id, 'set': "$set"}
                subFile = "updateTemplate.js"

            #Todo delete this if after implementing all operations
            if subFile != "":
                #print apiName + " " + operationId +" " + pascalApi + " " + subFile + " " +link+ str(linkSplitted)
                templatePath = "templates/"+subFile
                substituted = substituteVariables(templatePath, dictionary)
                if substituted is not None:
                    serviceFile = open("controllers/"+pascalApi+"Service.js", 'a')
                    serviceFile.write(substituted)
                    serviceFile.close()
                else:
                    print(" An Error occured while substituting variables!")
                    print(" The failing operation was" + operationId)
    return existingFiles

##------------------------------------------------------------------------------
#
#
def changeSwagger(yamlDoc, host):
    yamlDoc['host'] = host
    yamlDoc['schemes'] = "https"
    yamlDoc['basePath'] = "/docs"
    yamlDoc['info']['version'] = subversionExtender(yamlDoc['info']['version'])

    #PyYAML uses an alphabetically ordered dictionary, therefore the output
    # is in an alphabet order as well and not in the original order
    with open('api/swagger.yaml', 'w') as outfile:
        yaml.dump(yamlDoc, outfile, default_flow_style=False)


##------------------------------------------------------------------------------
#
#
def main():
    #urlHost = nameHost+".mybluemix.net"
    yamlDoc = []
    print "Program has been started"

    if applicationName == "" or nameHost == "":
        print " -applicationName and nameHost have to be DEFINED before running the application!"
        print "Program finished unsuccessfully"
        return 0

    createManifest(applicationName, nameHost)
    print " -created manifest.yml"
    editPackage()
    print " -changed dependencies in package.json"

    with open("api/swagger.yaml") as stream:
        try:
            yamlDoc = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if any(yamlDoc):
        filenames = createApiServices(yamlDoc)
        print " -all ApiService.js files have been changed. The are now connected to mongodb"
        changeParameters(filenames)
        print " -parameter of Api.js files have been changed"
        #This function is changing the swagger file. All quotation have been remove, which causes problems on bluemix
        #changeSwagger(yamlDoc, urlHost)
    else:
        print "Yaml Doc could not be opened, createAPIServices and changeSwagger aren't executed!"

    print "The program finished!"

main()
