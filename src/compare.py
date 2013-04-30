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
    plt.ylim(0,1)
    plt.title(title)
    plt.show()

def mymode(dist):
    max=0
    maxkey=""
    for key in dist.keys():
        if dist[key]>max:
            max=dist[key]
            maxkey = key
    return maxkey


if __name__ =="__main__":

    files={"N":"index.noun.synonyms.filtered","V":"index.verb.synonyms.filtered","J":"index.adj.synonyms.filtered","R":"index.adv.synonyms.filtered"}
    parameters=conf.configure(sys.argv)

     #read synsets = GS
    myfilter={}
    gstotal=0
    inwords=[]
    for pos in parameters["pos"]:
        filename=parameters["out"]+files[pos]
        myfilter[pos]=filter.Filter([],filename,inwords)
        gstotal+=myfilter[pos].total
        inwords=myfilter[pos].inwords

    print "Total synonym lists for evaluation is "+str(gstotal)

        #read simcache = thesaurus
    infile = parameters["simsfile"]

    adja = 1 #adja and adjb not used in this program
    adjb = 1

    iterations=0
    while(iterations<2):
        k = 100 #max number of neighbours to consider
        kstep=-10
        sim =0
        if parameters["metric"]=="linadj":
            simstep=0.1
        else:
            simstep=0.01
        if iterations == 1:
            k=1000

        mythes=thesaurus.Thesaurus(infile,infile,True,parameters["windows"],k,adja,adjb)
        thesaurus.Thesaurus.byblo=parameters["byblo"]
        #mythes.readvectors() #won't actually read vectors as simcached = True
        mythes.filter=True
        mythes.filterwords=inwords
        mythes.allpairssims(parameters["metric"]) #this will reload cached values


        currentk=k
        currentsim=sim
        recall={}
        precision={}
        fscore={}
        averagek={}
        minkset={}
        maxkset={}
        modek={}
        while currentk>0:

            if iterations==0:
                mythes.topk(currentk)
            else:
                mythes.topsim(currentsim)
            count=0
            totalrecall=0
            totalprecision=0
            totalintersect=0
            totaltarget=0
            totalproduced=0
            totalf=0
            totalk=0
            mink=1000
            maxk=0
            kvaluedist={}
            for thisvector in mythes.vectordict.values():
                thisword = thisvector.word
                thispos = thisvector.pos
                #print(thisword,thispos)
                #print myfilter[thispos].infile
                gs = myfilter[thispos].returnsyns(thisword+'/'+thispos)
                #print gs
                if len(gs) > 0:
                    #rec = thisvector.evaluaterecall(gs)
                    #totalrecall+=rec
                    #prec = thisvector.evaluateprecision(gs)
                    #totalprecision+=prec
                    (intersect,target)=thisvector.evaluaterecall2(gs)
                    (intersect2,produced)=thisvector.evaluateprecision2(gs)
                    if intersect==intersect2:
                        rec=intersect*1.0/target
                        if produced > 0:
                           prec=intersect*1.0/produced
                        else:
                           prec =0
                        totalrecall+=rec
                        totalprecision+=prec
                        totalintersect+=intersect
                        totaltarget+=target
                        totalproduced+=produced

                    else:
                        print "Error: intersects should be same size on precision and recall for "+thisword
                        exit(1)
                    if rec*prec>0:
                        fs=2*rec*prec/(rec+prec)
                    else:
                        fs=0
                    totalf+=fs
                    thisk=thisvector.getk()
                    totalk+=thisk
                    if thisk in kvaluedist.keys():
                        kvaluedist[thisk]+=1
                    else:
                        kvaluedist[thisk]=1
                    if thisk>maxk:
                        maxk=thisk
                    if thisk<mink:
                        mink=thisk
                    count+=1
            if totalrecall*totalprecision > 0:
                itrecall=totalintersect*1.0/totaltarget
                itprecision=totalintersect*1.0/totalproduced
                itf=itrecall*itprecision*2.0/(itrecall+itprecision)
                if iterations==0:
                    #recall[currentk]=totalrecall*1.0/count
                    #precision[currentk]=totalprecision*1.0/count
                    #fscore[currentk]=totalf*1.0/count
                    recall[currentk]=itrecall
                    precision[currentk]=itprecision
                    fscore[currentk]=itf
                    print currentk, itrecall,itf
                else:
                    #recall[currentsim]=totalrecall*1.0/count
                    #precision[currentsim]=totalprecision*1.0/count
                    #fscore[currentsim]=totalf*1.0/count
                    averagek[currentsim]=totalk*1.0/count
                    recall[currentsim]=itrecall
                    precision[currentsim]=itprecision
                    fscore[currentsim]=itf
                    #modek[currentsim]=mymode(kvaluedist)
                    #minkset[currentsim]=mink
                    #maxkset[currentsim]=maxk
                    #print currentsim, recall[currentsim],fscore[currentsim],averagek[currentsim], modek[currentsim], mink, maxk
                    print currentsim,itrecall,itf,averagek[currentsim]
            if currentk<25:
                kstep=-1
            if currentsim>0.25:
                if parameters["metric"]=="linadj":
                    if currentsim>0.6:
                        simstep=0.01
                else:
                    simstep=0.1

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
            if fscore[k] > peakf:
                peakf=fscore[k]
                peakfatk=k
            yfscore.append(fscore[k])
        x=numpy.array(xx)
        yr=numpy.array(yrecall)
        yp=numpy.array(yprecision)
        yf=numpy.array(yfscore)
        if iterations==0:
            mytitle="Recall, Precision and F Against k for "+parameters["metric"]+" with "+parameters["features"]+" features"
        else:
            mytitle="Recall, Precision and F Against sim threshold for "+parameters["metric"]+" with "+parameters["features"]+" features"
        print "Peak value of F is "+str(peakf)+" at x = "+str(peakfatk)
        print "Corresponding recall = "+str(recall[peakfatk])
        print "Corresponding precision = "+str(precision[peakfatk])
        if iterations==1:
            print "Corresponding average k = "+str(averagek[peakfatk])
        show(x,yr,yp,yf,mytitle)
        iterations+=1


