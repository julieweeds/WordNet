__author__ = 'Julie'

def configure(arguments):

    parameters={}
#set defaults
#location
    parameters["on_apollo"]=False
    parameters["at_home"]=False
#metric
    parameters["metric"]="cosine"
#feature type
    parameters["features"]="deps"


    for argument in arguments:

        if argument == "on_apollo":
            parameters["on_apollo"]=True
            parameters["at_home"]=False
            parameters["local"]=False
        if argument == "local":
            parameters["on_apollo"]=False
            parameters["at_home"]=False
            parameters["local"]=True
        if argument == "at_home":
            parameters["on_apollo"]=False
            parameters["at_home"] =True
            parameters["local"]=False
        if argument == "cosine":
            parameters["metric"]="cosine"
        if argument == "lin":
            parameters["metric"]="lin"
        if argument == "linadj":
            parameters["metric"]="linadj"
        if argument == "windows":
            parameters["features"]="win"
        if argument == "deps":
            parameters["features"]="dep"


    parameters = setfilenames(parameters)
    if parameters["features"]=="win":
        parameters["windows"]=True
    else:
        parameters["windows"]=False

    return parameters

def setfilenames(parameters):

    if parameters["at_home"]:
        parameters["parent"] ="C:/Program Files/WordNet/2.1/dict/"
        parameters["out"]="C:/Users/Julie/Documents/Github/WordNet/data/"
    if parameters["local"]:
        parameters["parent"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/2.1/dict/"
        parameters["out"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/data/"
        parameters["simsdir"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/STS/data/trial/STS2012-train/"
    parameters["simsfile"]=parameters["simsdir"]+parameters["metric"]+"_"+parameters["features"]+"_sims.cached"


    return parameters

