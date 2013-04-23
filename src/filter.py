__author__ = 'juliewe'
#take wordnet synsets and list of words from simcache and filter synsets
import conf
import sys


class Filter:

    def __init__(self,words,filename,inwords):
        self.infile=filename
        self.outfile=filename+".filtered"
        self.words=words
        self.total=0
        self.synsets={}
        self.filteredsets={}
        self.inwords=self.readfile(inwords)


    def readfile(self,inwords):
        instream=open(self.infile,'r')
        linesread=0
        for line in instream:
            l=line.rstrip()
            words = l.split("\t")
            words.reverse()
            word = words.pop()
            inwords.append(word)
            self.synsets[word]=[]
            for syn in words:
                if syn in self.synsets[word]:
                    #ignore duplicates
                    check=True
                else:
                    self.synsets[word].append(syn)
            linesread+=1
   #         print self.synsets[word]
        instream.close()
        print "Read "+str(linesread)+" lines from "+self.infile
        self.total=linesread
#        print self.synsets.keys()
        return inwords

    def applyfilter(self):

        done =0
        kept = 0
        for word in self.synsets.keys():
            if word in self.words:
                synonyms=self.synsets[word]
                filteredsyns=[]
                for synonym in synonyms:
                    if synonym in self.words:
                        filteredsyns.append(synonym)
                if len(filteredsyns)>0:
                    self.filteredsets[word]=filteredsyns
                    kept +=1
            else:
                print "Rejected "+word
            done+=1
        print "Applied filter to "+str(done)+" words and kept "+str(kept)


    def output(self):
        outstream=open(self.outfile,'w')
        done=0
        for word in self.filteredsets.keys():
            outstream.write(word)
            for syn in self.filteredsets[word]:
                outstream.write("\t"+syn)
            outstream.write("\n")
            done+=1

        outstream.close()
        print "Written "+str(done)+" sets to "+self.outfile

    def returnsyns(self,word):
    #    print self.synsets.keys()
        if word in self.synsets.keys():
            return self.synsets[word]
        else:
            return []

if __name__ =="__main__":

    files={"N":"index.noun.synonyms","V":"index.verb.synonyms","J":"index.adj.synonyms","R":"index.adv.synonyms"}
    parameters=conf.configure(sys.argv)

    #read simcache
    infile = parameters["simsfile"]
    words=[]
    instream=open(infile,'r')
    for line in instream:
        l=line.rstrip()
        fields=l.split("\t")
        words.append(fields[0])
    print "Read "+infile+" and added "+str(len(words))+" words to inclusion list"



    #apply filter to synsets
    for file in files.values():
        filename=parameters["out"]+file
        myfilter=Filter(words,filename,[])
        myfilter.applyfilter()
        myfilter.output()