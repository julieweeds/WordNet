__author__ = 'juliewe'

import sys

def filterfile(infile,pos,outfile):

    with open(infile) as instream:
        with open(outfile,'w') as outstream:
            for line in instream:
                fields=line.split('\t')
                subfields=fields[0].split('/')
                if len(subfields)==2:
                    if subfields[1]==pos:
                        outstream.write(line)

def separate(directory,infile):
    firstorder=directory+"firstorder.events.strings"
    secondorder=directory+"secondorder.events.strings"
    with open(firstorder,'w') as outstream1:
        with open(secondorder,'w') as outstream2:
            with open(directory+infile) as instream:
                for line in instream:
                    line.rstrip()
                    fields=line.split('\t')
                    word=fields[0]
                    outstream1.write(word)
                    outstream2.write(word)
                    features=fields[1:]
                    features.reverse()
                    while len(features)>0:
                        feat=features.pop()
                        freq=features.pop()
                        if isHigherOrder(feat):
                            outstream2.write("\t"+feat+"\t"+str(freq))
                        else:
                            outstream1.write("\t"+feat+"\t"+str(freq))


def isHigherOrder(feat):
    return findOrder(feat)>1

def findOrder(feat):
    parts=feat.split(":")
    return len(parts)-1


if __name__=="__main__":

    parentdir="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/thesdata/pilot/"
    vectorfile="vectors.ANs.deps.CONSTITUENTS"
    outfile="vectors.adjs"

    if sys.argv[1]=="filter":
        print "Filtering"
        filterfile(parentdir+vectorfile,"J",parentdir+outfile)
    elif sys.argv[1]=="separate":
        print "Separating orders"
        separate(parentdir,outfile)