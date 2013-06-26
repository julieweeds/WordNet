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
        self.ancestorlist=[]
        self.parent=[]
        self.definition=""

    def addWord(self,word):
        self.words.append(word)

    def addDataWords(self,no_syns,syns):
        if no_syns==len(self.words):
            #validity check
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
    def addDef(self,defin):
        for term in defin:
            self.definition+=" "+term

    def getParent(self):
        if len(self.parent)==0:
            for (rel,synset) in self.linklist:
                if rel =="@":
                    self.parent.append(synset)
            if SynsetEntry.verbose and len(self.parent)>1:
                print "Warning: "+self.sid+" has "+str(len(self.parent))+" parents"
            if len(self.parent) ==0:
                self.parent=["__TOP__"]
        return self.parent

    def getAncestors(self,synsetDict):
        #this is a list of lists.  Each list is a chain of ancestors from __TOP__ to synset
        if len(self.ancestorlist)==0:
            parents = self.getParent() #returns list of parents
            if parents==["__TOP__"]:
                self.ancestorlist=[parents]
            else:
                for parent in parents:
                    if parent not in synsetDict.keys():
                        if SynsetEntry.verbose: print "Warning: synsetDict not complete for "+parent
                        self.ancestorlist=[["__TOP__",parent]]
                    else:
                        #list of lists for ancestor
                        for innerlist in synsetDict[parent].getAncestors(synsetDict):
                            alist=list(innerlist)
                            alist.append(parent)
                            self.ancestorlist.append(alist)
        return self.ancestorlist

    def distance(self,aSynsetEntry):
        #compare self.ancestorlist and aSynsetEntry's ancestorlist to find lowest common ancestor
        #assumes "tree has been made"


        mindistance=float("inf")

        for alist in self.ancestorlist:
            for blist in aSynsetEntry.ancestorlist:
                clist=[] #to store common ancestors
                dlist=[] #to store separating ancestors
                for item in alist:
                    if item in blist:
                        clist.append(item)
                    else:
                        dlist.append(item)
                for item in blist:
                    if item not in alist:
                        dlist.append(item)
                if len(clist)<2:
                    #only commonality is __TOP__
                    distance=float("inf")
                else:

                    distance=len(dlist)
                    #print dlist,distance
                if distance < mindistance:
                    mindistance=distance
        return mindistance

    def toString(self):
        res = self.sid
        for word in self.words:
            res+="\t"+word
        res+="\t"+self.definition+"\n"
        for (type,lid) in self.linklist:
            res+="\t"+type+":"+lid
        res+= str(self.ancestorlist)
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
                    self.synsetdict[synset].addDef(rest)

                    if linesread%10000==0:
                        print "Read "+str(linesread)+" lines"
                        break
        print "Completed: Read "+str(linesread)+" lines"
        self.makeTree()

    def makeTree(self):
        print "Making tree ...."
        done=0
        for synset in self.synsetdict.keys():
            self.synsetdict[synset].getAncestors(self.synsetdict)
            done+=1
            if done %1000 ==0: print "Processed "+str(done)+" entries"

        print "Finished making tree."

    def readcounts(self):
        return

    def displaySynsets(self,word):
        if word in self.worddict.keys():
            print self.worddict[word].toString()
            for sense in self.worddict[word].senselist:
                print self.synsetdict[sense].toString()
        else:
            print word +" not found in dictionary"

    def findwords(self,nosenses):
        #displayed=0
        candidates=[]
        for word in self.worddict.keys():
            if self.worddict[word].senses==nosenses:
                #print self.worddict[word].toString()
                length=len(self.worddict[word].senselist)
                found=0
                shouldfind=0
                totaldist=0
                for i in range(length):
                    sense=self.worddict[word].senselist[i]
                    if sense in self.synsetdict.keys():
                        #print self.synsetdict[sense].toString()
                        for j in range(i+1,length):
                            sense2=self.worddict[word].senselist[j]
                            dist=self.synsetdict[sense].distance(self.synsetdict[sense2])
                            #print sense,sense2,str(dist)
                            shouldfind+=1
                            if dist < float("inf"):
                                #displayed+=1
                                found+=1
                                totaldist+=dist
                if found == shouldfind:
                    average=float(totaldist)/float(found)
                    candidates.append((average,word))
            #if displayed>0: break
        candidates.sort(reverse=True)
        print "There are "+str(len(candidates))+" in candidate list for "+str(nosenses)+" senses, top 10 are: "
        self.displaycandidates(candidates[0:10])
        #print candidates[0:10]
        return candidates

    def displaycandidates(self,mylist):

        for (distance,word) in mylist:
            print word, distance
            print self.worddict[word].toString()
            for sid in self.worddict[word].senselist:
                print self.synsetdict[sid].toString()

if __name__ =="__main__":

    words=[("accusation","N"),("ancylus","N")]
    parameters=conf.configure(sys.argv)
    trees={}
    for pos in parameters["pos"]:
        trees[pos]=Tree(pos,parameters["data"])
    #for (word,pos) in words:
    #    trees[pos].displaySynsets(word)
    for i in range(2,6):
        trees["N"].findwords(i)
