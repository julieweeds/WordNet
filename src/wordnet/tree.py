__author__ = 'Julie'

import conf,sys,re

class WordEntry:
    verbose=False

    def __init__(self,word,senses):

        self.word=word
        self.senses=senses
        self.senselist=[] #accumulated in reverse order and then reversed


    def addSynset(self,sid):
        if len(self.senselist)<self.senses:
            self.senselist.append(sid)
            if len(self.senselist)==self.senses:
                self.senselist.reverse()
        else:
            print "Error: "+self.word +" already has listed number of senses"

    def toString(self):
        res = self.word + "\t"+str(self.senses)
        for sense in self.senselist:
            res = res + "\t"+sense
        #res=res+"\n"
        return res

class SynsetEntry:

    verbose=False
    def __init__(self,sid):
        self.sid=sid
        self.words=[]
        self.no_links=0
        self.linklist=[]

    def addWord(self,word):
        self.words.append(word)

    def addDataWords(self,no_syns,syns):
        if no_syns==len(self.words):
            #validity chech
            return
        elif no_syns<len(self.words):
            if SynsetEntry.verbose:
                print "Data error: "+self.sid+" already has "+str(len(self.words))+" words and listed as having "+str(no_syns)
        else:
            if SynsetEntry.verbose:
                print "Data error: "+self.sid+" has  "+str(len(self.words))+" words but should have "+str(no_syns)+" ... adding"
            for i in range(no_syns):
                if syns[i*2] not in self.words:
                    self.words.append(syns[i*2])

    def addLinks(self,no_links,links):
        self.no_links=no_links
        for i in range(self.no_links):
            type=links[i*4]
            lid=links[i*4+1]
            self.linklist.append((type,lid))

    def toString(self):
        res = self.sid
        for word in self.words:
            res+="\t"+word
        res+="\n"
        for (type,lid) in self.linklist:
            res+="\t"+type+":"+lid
        return res

class Tree:
    indexfiles={"N":"index.noun","V":"index.verb","J":"index.adj","R":"index.adv"}
    datafiles={"N":"data.noun","V":"data.verb","J":"data.adj","R":"data.adv"}
    cntfile="cntlist.rev"

    def __init__(self,pos,datadir,verbose=False):
        self.pos=pos
        self.datadir=datadir
        self.worddict={} #to hold mapping from word to wordentry containing sense info
        self.synsetdict={} #to hold mapping from synset id to synsetentry containing tree links
        self.verbose=verbose
        WordEntry.verbose=verbose
        SynsetEntry.verbose=verbose

        ###read files
        self.readindex()
        self.readdata()
        self.readcounts()

    def readindex(self):
        filename=self.datadir+Tree.indexfiles[self.pos]
        print "Reading "+filename
        linesread=0
        with open(filename,'r') as instream:
            for line in instream:
                linesread+=1
                if linesread>30: #ignore header
                    line = line.rstrip().lower()
                    fields=line.split(' ')
                    word=fields[0]
                    senses=int(fields[2])
                    self.worddict[word]=WordEntry(word,senses)
                    while senses>0:
                        #print word,senses
                        synsetid=fields.pop()
                        self.worddict[word].addSynset(synsetid)
                        if synsetid in self.synsetdict.keys():
                            self.synsetdict[synsetid].addWord(word)
                        else:
                            self.synsetdict[synsetid]=SynsetEntry(synsetid)
                            self.synsetdict[synsetid].addWord(word)
                        senses=senses-1
                    if linesread%10000==0:
                        print "Read "+str(linesread)+" lines"
                        break
        print "Completed: Read "+str(linesread)+" lines"

    def readdata(self):

        filename=self.datadir+Tree.datafiles[self.pos]
        print "Reading "+filename
        linesread=0
        with open(filename,'r') as instream:
            for line in instream:
                linesread+=1
                if linesread>30: #ignore header

                    line = line.rstrip().lower()
                    fields=line.split(' ')
#                    print fields
                    synset=fields[0]
                    no_syns=int(fields[3],16) #hex!!
                    syns=fields[4:no_syns*2+4]
                    no_links=int(fields[no_syns*2+4])
                    links=fields[no_syns*2+5:no_syns*2+5+no_links*4]
                    rest= fields[no_syns*2+5+no_links*4:len(fields)]
                   # print synset
                   # print str(no_syns),syns
                   # print str(no_links),links
                   # print rest
                    if synset not in self.synsetdict.keys(): #shouldn't need this if complete index read in
                        if self.verbose:
                            print "Warning: not seen in index: "+synset
                        self.synsetdict[synset]=SynsetEntry(synset)
                    self.synsetdict[synset].addDataWords(no_syns,syns) #shouldn't need this if files valid
                    self.synsetdict[synset].addLinks(no_links,links)

                    if linesread%10000==0:
                        print "Read "+str(linesread)+" lines"
                        break
        print "Completed: Read "+str(linesread)+" lines"


    def readcounts(self):
        return

    def displaySynsets(self,word):
        if word in self.worddict.keys():
            print self.worddict[word].toString()
            for sense in self.worddict[word].senselist:
                print self.synsetdict[sense].toString()
        else:
            print word +" not found in dictionary"


if __name__ =="__main__":

    words=[("accusation","N"),("ancylus","N")]
    parameters=conf.configure(sys.argv)
    trees={}
    for pos in parameters["pos"]:
        trees[pos]=Tree(pos,parameters["data"])
    for (word,pos) in words:
        trees[pos].displaySynsets(word)
