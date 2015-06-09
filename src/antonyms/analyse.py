__author__ = 'juliewe'

import sys
from conf import configure

class ThesEntry:

    def __init__(self,name):
        self.name=name
        self.sims={}
        self.neighbours=[]

    def addneigh(self,word,sim):
        self.sims[word]=sim
        self.neighbours.append(word)

    def addneighs(self, neighlist):

        neighlist.reverse()
        while len(neighlist)>0:
            neigh=neighlist.pop().split('/')[0]
            sim=neighlist.pop()
            self.addneigh(neigh,sim)

    def getRank(self,word):
        nlist=list(self.neighbours)
        nlist.reverse()
        count=0
        found=False
        while len(nlist) > 0 and found==False:
            count+=1
            if nlist.pop()==word:
                found=True
        if found:
            return count
        else:
            return 1001

class Thesaurus:

    def __init__(self,thesfile,parameters):
        self.name=thesfile
        self.parameters=parameters
        self.entries={}
        self.loadthesfile()

    def loadthesfile(self):
        filename=self.parameters["parentdir"]+self.parameters["thesdir"]+self.name
        with open(filename) as instream:
            for line in instream:
                line=line.rstrip()
                fields=line.split('\t')
                word=fields[0].split('/')[0]
                neighbours=fields[1:]
                entry=ThesEntry(word)
                entry.addneighs(neighbours)
                self.entries[word]=entry

    def getSim(self,word1,word2):

        return self.entries[word1].sims[word2]

    def getRank(self,word1,word2):
        return self.entries[word1].getRank(word2)

class Analyser:

    def __init__(self,parameters):
        self.parameters=parameters

        self.thesauruses={}
        for filename in self.parameters["thesfiles"]:
            self.thesauruses[filename]=Thesaurus(filename,self.parameters)



    def processlist(self,filename,thes):

        with open(self.parameters["parentdir"]+self.parameters["testdatadir"]+filename) as instream:

            totalsim=0
            totalrank=0
            count=0
            for line in instream:
                line=line.rstrip()
                pair=line.split('\t')
                count+=1
                totalsim+=float(thes.getSim(pair[0],pair[1]))
                totalrank+=thes.getRank(pair[0],pair[1])

            avsim=totalsim/count
            avrank=totalrank/count

        print "Average similarity on "+filename+" with "+thes.name+" is "+str(avsim)
        print "Average rank on "+filename+" with "+thes.name+" is "+str(avrank)

    def run(self):
        for thes in self.thesauruses.values():
            self.processlist(self.parameters["synonymfile"],thes)
            self.processlist(self.parameters["antonymfile"],thes)

if __name__=="__main__":
    myAnalyser=Analyser(configure(sys.argv))
    myAnalyser.run()