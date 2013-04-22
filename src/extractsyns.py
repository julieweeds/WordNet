__author__ = 'Julie'

import conf
import sys
import re

class Index:

    multiwordPATT = re.compile('.*_.*')
    def __init__(self,pos,filename,outname):

        self.pos=pos
        self.filename=filename
        self.outname=outname
        self.words={}
        self.synsets={}
        self.readfile()
        self.outputall()

    def readfile(self):

        instream=open(self.filename,'r')
        linesread=0
        for line in instream:
            linesread+=1
            if linesread>30:  #ignore first 30 lines as header
                self.processline(line.rstrip())
        instream.close()
        print "Read "+str(linesread)+" lines from "+self.filename

    def processline(self,line):

        fields = line.split(' ')
#        length=len(fields)
#        senses=length-10
 #       print fields
        word = fields[0]+"/"+self.pos
 #       print word +" : "+str(len(fields))
        senses = int(fields[2])
        while senses>0:
            synset=fields.pop()
            if self.checknotmulti(word): #ignore multiword expressions
                self.add(word,synset)
            senses-=1

    def checknotmulti(self,word):
        matchobj=Index.multiwordPATT.match(word)
        if matchobj:
            return False
        else:
            return True

    def add(self,word,synset):
#        print "Adding "+word+" : "+synset
        if word in self.words.keys():
            self.words[word].append(synset)
        else:
            self.words[word]=[synset]

        if synset in self.synsets.keys():
            self.synsets[synset].append(word)
        else:
            self.synsets[synset]=[word]

    def output(self,word,outstream):

        list=[]
        for synset in self.words[word]:
            for synonym in self.synsets[synset]:
                if synonym == word:
                    #ignore word itself
                    check=True
                else:
                    list.append(synonym)
        if len(list)>0:
            outstream.write(word)
            for synonym in list:
                outstream.write("\t"+synonym)
            outstream.write("\n")

    def outputall(self):

        outstream=open(self.outname,'w')

        done=0
        for word in self.words.keys():
#            print word
            self.output(word,outstream)
            done+=1
        outstream.close()
        print "Written "+str(done)+" synsets to "+self.outname

if __name__ =="__main__":

    files={"N":"index.noun","V":"index.verb","J":"index.adj","R":"index.adv"}
    parameters=conf.configure(sys.argv)
    indexdict={}

    for pos in files.keys():
        filename=parameters["parent"]+files[pos]
        outname=parameters["out"]+files[pos]+".synonyms"
        indexdict[file]=Index(pos,filename,outname)

