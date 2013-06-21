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
        if argument == "byblo":
            parameters["byblo"]=True
        if argument =="nouns":
            parameters["pos"]=["N"]
        if argument =="adjusted_sims":
            parameters["adjusted_sims"]=True
            parameters["byblo"]=True
        if argument =="adjusted_neighs":
            parameters["adjusted_neighs"]=True
            parameters["byblo"]=True


    parameters = setfilenames(parameters)

    return parameters

def setfilenames(parameters):

    if parameters["at_home"]:
        parameters["data"] ="C:/Users/Julie/Documents/GitHub/WordNet/dict/"
    if parameters["local"]:
        parameters["data"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/2.1/dict/"


    return parameters

