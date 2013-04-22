__author__ = 'Julie'

def configure(arguments):

    parameters={}
#set defaults
#location
    parameters["on_apollo"]=False
    parameters["at_home"]=False

    for argument in arguments:

        if argument == "on_apollo":
            parameters["on_apollo"]=True
            parameters["at_home"]=False
        if argument == "local":
            parameters["on_apollo"]=False
            parameters["at_home"]=False
        if argument == "at_home":
            parameters["on_apollo"]=False
            parameters["at_home"] =True

    parameters = setfilenames(parameters)

    return parameters

def setfilenames(parameters):

    if parameters["at_home"]:
        parameters["parent"] ="C:/Program Files/WordNet/2.1/dict/"
        parameters["out"]="C:/Users/Julie/Documents/Github/WordNet/data/"



    return parameters

