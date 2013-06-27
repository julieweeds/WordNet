__author__ = 'Julie'

def configure(arguments):

    parameters={}
    #set defaults
    #location
    parameters["on_apollo"]=False
    parameters["at_home"]=True
    parameters["local"]=False
        #POS
    parameters["pos"]=["N"]
    parameters["testing"]=False



    for argument in arguments:

        if argument == "on_apollo":
            parameters["on_apollo"]=True
            parameters["at_home"]=False
            parameters["local"]=False
        elif argument == "local":
            parameters["on_apollo"]=False
            parameters["at_home"]=False
            parameters["local"]=True
        elif argument == "at_home":
            parameters["on_apollo"]=False
            parameters["at_home"] =True
            parameters["local"]=False
        elif argument == "testing":
            parameters["testing"]=True


    parameters = setfilenames(parameters)

    return parameters

def setfilenames(parameters):

    if parameters["at_home"]:
        parameters["data"] ="C:/Users/Julie/Documents/GitHub/WordNet/dict/"
    if parameters["local"]:
        parameters["data"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/dict/"


    return parameters

