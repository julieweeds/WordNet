__author__ = 'juliewe'

def configure(arguments):
    parameters={}
    #parameters["testdatadir"]="moredata/"
    parameters["parentdir"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/"
    parameters["thesdir"]="thesdata/antopilot/"
    parameters["testdatadir"]=parameters["thesdir"]

    parameters["thesfiles"]=["firstorder_pmi.sims.neighbours.strings","secondorder_pmi.sims.neighbours.strings"]
    parameters["antonymfile"]="wikiPOS_adjs_ants.txt"
    parameters["synonymfile"]="wikiPOS_adjs_syns.txt"

    return parameters