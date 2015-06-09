__author__ = 'juliewe'

import sys,math

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
                    line=line.rstrip()
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
                    outstream1.write('\n')
                    outstream2.write('\n')


def isHigherOrder(feat):
    return findOrder(feat)>1

def findOrder(feat):
    parts=feat.split(":")
    return len(parts)-1

def maketotals(directory,infile):
    parts=infile.split(".")
    rowfile=parts[0]+".entries."+parts[2]
    colfile=parts[0]+".features."+parts[2]
    with open(directory+infile) as instream:
        with open(directory+rowfile,'w') as rowstream:
            with open(directory+colfile,'w') as colstream:
                featdict={}
                for line in instream:
                    line=line.rstrip()
                    fields=line.split('\t')
                    word=fields[0]
                    features=fields[1:]
                    features.reverse()
                    rowtotal=0
                    while len(features)>0:
                        feat=features.pop()
                        freq=features.pop()
                        rowtotal+=float(freq)
                        featdict[feat]=featdict.get(feat,0)+float(freq)
                    rowstream.write(word+"\t"+str(rowtotal)+"\n")

                for feat in featdict.keys():
                    colstream.write(feat+"\t"+str(featdict[feat])+"\n")

def makepmi(directory,infile):
    parts=infile.split(".")
    rowfile=parts[0]+".entries."+parts[2]
    colfile=parts[0]+".features."+parts[2]
    pmifile=parts[0]+"_pmi.events."+parts[2]

    rowtotals=readtotals(directory,rowfile)
    coltotals=readtotals(directory,colfile)
    gt = findtotal(rowtotals)

    with open(directory+infile) as instream:
        with open(directory+pmifile,'w') as outstream:
            for line in instream:
                line=line.rstrip()
                fields=line.split('\t')
                word=fields[0]
                features=fields[1:]
                features.reverse()
                found=0
                while len(features)>0:
                    feat=features.pop()
                    freq=float(features.pop())
                    pmi=math.log((freq*gt)/(rowtotals[word]*coltotals[feat]))
                    if pmi>0:
                        found+=1
                        if found==1:
                            outstream.write(word)
                        outstream.write("\t"+feat+"\t"+str(pmi))
                if found>0:
                    outstream.write("\n")


def readtotals(directory,filename):
    totals={}
    with open(directory+filename) as instream:
        for line in instream:
            line = line.rstrip()
            fields=line.split('\t')
            totals[fields[0]]=float(fields[1])
    return totals

def findtotal(featdict):
    total=0
    for key in featdict.keys():
        total+=featdict[key]
    return total

if __name__=="__main__":

    parentdir="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/thesdata/antopilot/"
    vectorfile="vectors.ANs.deps.CONSTITUENTS"
    outfile="higherorder.events.strings"

    if sys.argv[1]=="filter":
        print "Filtering"
        filterfile(parentdir+vectorfile,"J",parentdir+outfile)
    elif sys.argv[1]=="separate":
        print "Separating orders"
        separate(parentdir,outfile)
    elif sys.argv[1]=="maketotals":
        print "Making totals for "+parentdir+sys.argv[2]
        maketotals(parentdir,sys.argv[2])
    elif sys.argv[1]=="makepmi":
        print "Making pmi file for "+parentdir+sys.argv[2]
        makepmi(parentdir,sys.argv[2])