__author__ = 'juliewe'

import thesaurus
import conf
import sys
import filter
import numpy
import matplotlib.pyplot as plt

def show(x,yr,yp,yf,title):
#    xp=numpy.linspace(0,1,100)
    plt.plot(x,yr,'.',x,yp,'x',x,yf,'o')
    plt.ylim(0,0.5)
    plt.title(title)
    plt.show()


if __name__ =="__main__":

    files={"N":"index.noun.synonyms.filtered","V":"index.verb.synonyms.filtered","J":"index.adj.synonyms.filtered","R":"index.adv.synonyms.filtered"}
    parameters=conf.configure(sys.argv)

     #read synsets = GS
    myfilter={}
    gstotal=0
    inwords=[]
    for pos in files.keys():
        filename=parameters["out"]+files[pos]
        myfilter[pos]=filter.Filter([],filename,inwords)
        gstotal+=myfilter[pos].total
        inwords=myfilter[pos].inwords

    print "Total synonym lists for evaluation is "+str(gstotal)

        #read simcache = thesaurus
    infile = parameters["simsfile"]
    k = 100 #max number of neighbours to consider
    kstep=-1
    sim =0
    simstep=-kstep*1.0/k
    adja = 1 #adja and adjb not used in this program
    adjb = 1

    iterations=1
    while(iterations<2):
        if iterations == 1:
            k=1000

        mythes=thesaurus.Thesaurus(infile,infile,True,parameters["windows"],k,adja,adjb)
        #mythes.readvectors() #won't actually read vectors as simcached = True
        mythes.filter=True
        mythes.filterwords=inwords
        mythes.allpairssims(parameters["metric"]) #this will reload cached values


        currentk=k
        currentsim=sim
        recall={}
        precision={}
        while currentk>0:

            if iterations==0:
                mythes.topk(currentk)
            else:
                mythes.topsim(currentsim)
            count=0
            totalrecall=0
            totalprecision=0
            for thisvector in mythes.vectordict.values():
                thisword = thisvector.word
                thispos = thisvector.pos
                #print(thisword,thispos)
                #print myfilter[thispos].infile
                gs = myfilter[thispos].returnsyns(thisword+'/'+thispos)
                #print gs
                if len(gs) > 0:
                    totalrecall += thisvector.evaluaterecall(gs)
                    totalprecision += thisvector.evaluateprecision(gs)
                    count+=1
            if iterations==0:
                recall[currentk]=totalrecall*1.0/count
                precision[currentk]=totalprecision*1.0/count
                print currentk, recall[currentk]
            else:
                recall[currentsim]=totalrecall*1.0/count
                precision[currentsim]=totalprecision*1.0/count
                print currentk, recall[currentsim]
            currentk+=kstep
            currentsim+=simstep

        xx=[]
        yrecall=[]
        yprecision=[]
        yfscore=[]
        peakf=0
        peakfatk=0
        for k in recall.keys():
            xx.append(k)
            yrecall.append(recall[k])
            yprecision.append(precision[k])
            fscore=2*recall[k]*precision[k]/(recall[k]+precision[k])
            if fscore > peakf:
                peakf=fscore
                peakfatk=k
            yfscore.append(fscore)
        x=numpy.array(xx)
        yr=numpy.array(yrecall)
        yp=numpy.array(yprecision)
        yf=numpy.array(yfscore)
        if iterations==1:
            mytitle="Recall, Precision and F Against k for "+parameters["metric"]+" with "+parameters["features"]+" features"
        else:
            mytitle="Recall, Precision and F Against sim threshold for "+parameters["metric"]+" with "+parameters["features"]+" features"
        print "Peak value of F is "+str(peakf)+" at x = "+str(peakfatk)
        print "Corresponding recall = "+str(recall[peakfatk])
        print "Corresponding precision = "+str(precision[peakfatk])
        show(x,yr,yp,yf,mytitle)
        iterations+=1


