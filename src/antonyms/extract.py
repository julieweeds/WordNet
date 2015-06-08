__author__ = 'juliewe'

#8th June 2015
#build lists of antonyms etc from WN
from nltk.corpus import wordnet as wn
import re

class Extractor:

    posdict={"J":wn.ADJ,"N":wn.NOUN}

    def __init__(self,testpos="J",testwords=[],testfile="",outfile=""):
        self.pos=Extractor.posdict[testpos]
        self.wordlist=testwords
        self.wordfile=testfile
        self.synonyms={}
        self.antonyms={}

        if len(self.wordlist)>0:
            self.processlist()

        elif testfile!="":
            self.makewordlist()
            self.processlist()

        self.synonyms=self.filter(self.synonyms)
        self.antonyms=self.filter(self.antonyms)
        self.output(self.synonyms,outfile+'syns.txt')
        self.output(self.antonyms,outfile+'ants.txt')

    def makewordlist(self):
        self.wordlist=[]
        count=0
        with open(self.wordfile) as instream:
            for line in instream:
                count+=1
                line.rstrip()
                fields=line.split('\t')
                subfields=fields[0].split("/")
                if len(subfields)>0:
                    self.wordlist.append(subfields[0])
                if count%10000==0:
                    print "Read "+str(count)+" lines"


    def processlist(self):
        count=0
        found=0
        for word in self.wordlist:
            found+=self.process(word)
            count+=1
            if count%10000==0:
                print "Found "+str(found)+" out of "+str(count)+" words"

        print "Found "+str(found)+" out of "+str(count)+" words"

    def process(self, word):
        synsets= wn.synsets(word,pos=self.pos)
        if len(synsets)>0:
            synset=synsets[0] #predominant sense

            lemmas=synset.lemmas
            if len(synset.lemmas)>1:
                for alemma in synset.lemmas:
                    if alemma.name != word:
                        currentlist=self.synonyms.get(word,[])
                        currentlist.append(alemma.name)
                        self.synonyms[word]=currentlist
            if len(synset.lemmas)>0:
                for alemma in synset.lemmas:
                    if alemma.name==word:
                        currentlist=self.antonyms.get(word,[])
                        for blemma in alemma.antonyms():
                            currentlist.append(blemma.name)
                        self.antonyms[word]=currentlist
            return 1
        else:
            return 0

    def filter(self,candidates):
        filtered={}
        for aword in candidates.keys():
            wordlist=candidates[aword]
            filteredlist=[]
            for bword in wordlist:
                checklist=candidates.get(bword,[])
                if aword in checklist:
                    filteredlist.append(bword)

            if len(filteredlist)>0:
                filtered[aword]=filteredlist
        return filtered

    def output(self,candidates,filename):
        with open(filename,'w') as outstream:
            for key in candidates.keys():
                for value in candidates[key]:
                    string = key+"\t"+value+"\n"
                    outstream.write(string)

if __name__ == "__main__":
    testwords=["hot","cold","bright","dull","warm","cool","fat","thin","thick","lively","tepid","lukewarm"]
    #testwords=["hot"]
    testpos="J"

    #parentdir="/Volumes/LocalScratchHD/juliewe/Documents/workspace/ThesEval/data/"
    #thesfiles={"J":"wikiPOS_t100f100_adjs_deps/neighbours.strings",
    #           "N":"wikiPOS_t100f100_nouns_deps/neighbours.strings"}
    #outdir="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/moredata/"

    outdir="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/thesdata/pilot/"
    parentdir=outdir
    thesfiles={"J":"vectors.adjs"}
    outfiles={"J":"wikiPOS_adjs_","N":"wikiPOS_nouns_"}


    myExtractor=Extractor(testpos=testpos,testfile=parentdir+thesfiles[testpos],outfile=outdir+outfiles[testpos])
