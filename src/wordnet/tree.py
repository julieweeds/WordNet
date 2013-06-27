__author__ = 'Julie'

import conf,sys,re
#from nltk.corpus import wordnet as wn

class WordEntry:
    verbose=False
  #  wnpos=wn.NOUN
    limit = 5 #maximum predominance of most frequent sense over least frequent sense

    def __init__(self,word,senses):

        self.word=word
        self.senses=senses
        self.senselist=[] #accumulated in reverse order and then reversed
        self.ratio=0
        self.freqs=[] #am not guarenteeing order is the same as in senselist


    def addSynset(self,sid):
        if len(self.senselist)<self.senses:
            self.senselist.append(sid)
            if len(self.senselist)==self.senses:
                self.senselist.reverse()
        else:
            print "Error: "+self.word +" already has listed number of senses"

    def addSenseFreq(self,freq):
        self.freqs.append(float(freq))

#    def checkSenses(self):
#        todelete=False
#        #print self.word,self.senses,wn.synsets(self.word,WordEntry.wnpos)
#        wnsenses=len(wn.lemmas(self.word,WordEntry.wnpos))
#        if wnsenses != self.senses:
#            print "Warning: number of senses mismatch for "+self.word+" : "+str(self.senses)+" compared to nltk: "+str(wnsenses)
#        #total=0
#        least=float("inf")
#        most=0
#
#        for lemma in wn.lemmas(self.word,WordEntry.wnpos):
#            #print lemma,lemma.count()
#            count=lemma.count()
#            if count<1:todelete=True  #delete any where one or more of the senses has not been seen
#            #total+=count
#            else:
#                if count>most:most=count
#                if count<least:least=count
#        ratio = most/least
#        self.ratio=ratio
#        if ratio>WordEntry.limit:todelete=True
#        return todelete

    def checkSenses(self):
        if len(self.freqs)<len(self.senselist): #unseen senses not recorded
            return True
        most = max(self.freqs)
        least = min(self.freqs)
        if least < 1:#unseen sense recorded as zero
            return True
        else:
            ratio = most/least
            self.ratio=ratio
            if ratio>WordEntry.limit:#overly predominant sense
                return True
        return False

    def toString(self):
        res = self.word + "\t no_of_senses = "+str(self.senses)+" \tmax to min sense predominance ratio = "+str(self.ratio)
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
        #for (type,lid) in self.linklist:
        #    res+="\t"+type+":"+lid
        #res+= str(self.ancestorlist)
        return res

class Tree:
    indexfiles={"N":"index.noun","V":"index.verb","J":"index.adj","R":"index.adv"}
    datafiles={"N":"data.noun","V":"data.verb","J":"data.adj","R":"data.adv"}
    cntfile="cntlist.rev"
    multiPATT=re.compile('.*_.*')
    nouncntPATT=re.compile('(.*)%1:')
    cntPATT={"N":re.compile('(.*)%1'),"V":re.compile('(.*)%2'),"J":re.compile('(.*)%3'),"R":re.compile('(.*)%4')}


    def __init__(self,pos,datadir,verbose=False):
        self.pos=pos
        self.datadir=datadir
        self.worddict={} #to hold mapping from word to wordentry containing sense info
        self.synsetdict={} #to hold mapping from synset id to synsetentry containing tree links
        self.verbose=verbose
        WordEntry.verbose=verbose
        SynsetEntry.verbose=verbose
        self.completeread=False

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
                        if self.verbose: print "Read "+str(linesread)+" lines"
                        if parameters["at_home"] or parameters["testing"]:break
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
                        if self.verbose: print "Read "+str(linesread)+" lines"
                        if parameters["at_home"] or parameters["testing"]:break
        print "Completed: Read "+str(linesread)+" lines"
        self.completeread=True
        self.makeTree()

    def makeTree(self):
        print "Making tree ...."
        done=0
        for synset in self.synsetdict.keys():
            self.synsetdict[synset].getAncestors(self.synsetdict)
            done+=1
            if done %1000 ==0 and self.verbose: print "Processed "+str(done)+" entries"

        print "Finished making tree."

#    def readcounts(self):
#        total=0
#        count=0
#        for word in self.worddict.keys():
#            total+=1
#            todelete = self.worddict[word].checkSenses()
#            if todelete:
#                count+=1
#                del self.worddict[word]
#        print "Deleted "+str(count)+" out of "+str(total)+" word entries due to no sense info or over-predominance of one sense"
#        return

    def readcounts(self):
        filename=self.datadir+Tree.cntfile
        print "Reading "+filename
        linesread=0
        with open(filename,'r') as instream:
            linesread+=1
            for line in instream:
                line = line.rstrip()
                fields=line.split(' ')
                if len(fields)!=3:
                    print "Invalid line "+line
                matchobj=Tree.cntPATT[self.pos].match(fields[0])
                if matchobj: #might not match if verb etc so ignore
                    word=matchobj.group(1)
                if word in self.worddict.keys(): #should be there but just in case
                    self.worddict[word].addSenseFreq(fields[2])
            if linesread%1000==0:
                if self.verbose: print "Read "+str(linesread)+" lines"
        print "Completed: read "+str(linesread)+" lines"
        print "Analysing sense frequency information"
        total=0
        count=0
        for word in self.worddict.keys():
            total+=1
            todelete = self.worddict[word].checkSenses()
            if todelete:
                count+=1
                del self.worddict[word]
        print "Deleted "+str(count)+" out of "+str(total)+" word entries due to no sense info or over-predominance of one sense"
        return


    def displaySynsets(self,word):
        if word in self.worddict.keys():
            print self.worddict[word].toString()
            for sense in self.worddict[word].senselist:
                print self.synsetdict[sense].toString()
        else:
            print word +" not found in dictionary"

    def findwords(self,nosenses):
        if nosenses==1:
            candidates=self.findmonos()
        #displayed=0
        else:
            candidates=[]
            for word in self.worddict.keys():
                if self.worddict[word].senses==nosenses:
                    #print self.worddict[word].toString()
                    length=len(self.worddict[word].senselist)
                    #found=0
                    #shouldfind=0
                    #totaldist=0
                    maxdist=float("inf")
                    for i in range(length):
                        sense=self.worddict[word].senselist[i]
                        if self.completeread or sense in self.synsetdict.keys():
                            #print self.synsetdict[sense].toString()
                            for j in range(i+1,length):
                                sense2=self.worddict[word].senselist[j]
                                dist=self.synsetdict[sense].distance(self.synsetdict[sense2])
                                #print sense,sense2,str(dist)
                                #shouldfind+=1
                                if dist < maxdist:
                                    #displayed+=1
                                    #found+=1
                                    #totaldist+=dist
                                    maxdist=dist
                    #if found == shouldfind:
                        #average=float(totaldist)/float(found)
                        #candidates.append((average,word))
                    candidates.append((maxdist,word))
                #if displayed>0: break
        candidates.sort(reverse=True)
        candidates=self.filtercandidates(candidates)
        print "There are "+str(len(candidates))+" in candidate list for "+str(nosenses)+" senses, up to top 20 are: "
        self.displaycandidates(candidates[0:20])
        #print candidates[0:10]
        return candidates

    def findmonos(self):
        candidates=[]
        for word in self.worddict.keys():
            if self.worddict[word].senses==1:
                if len(self.worddict[word].freqs)==1:
                    freq=self.worddict[word].freqs[0]
                    candidates.append((freq,word))
        return candidates

    def filtercandidates(self,mylist):
        #remove multiwords
        newlist=[]
        for(distance,word) in mylist:
            matchobj=Tree.multiPATT.match(word)
            if not matchobj:
                newlist.append((distance,word))
        return newlist

    def displaycandidates(self,mylist):

        for (distance,word) in mylist:
            print word+ ": score = "+str(distance)
            print self.worddict[word].toString()
            for sid in self.worddict[word].senselist:
                print self.synsetdict[sid].toString()

if __name__ =="__main__":

#    words=[("accusation","N"),("ancylus","N")]
    parameters=conf.configure(sys.argv)
    trees={}
    for pos in parameters["pos"]:
        trees[pos]=Tree(pos,parameters["data"],verbose=False)
    #for (word,pos) in words:
    #    trees[pos].displaySynsets(word)
    for i in range(1,10):
        trees["N"].findwords(i)
