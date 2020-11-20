import numpy as np
from collections import defaultdict
from math import log
from nltk import word_tokenize
class BM25Ranker:
    def __init__(self,index,N,k,b):
        self.index = index
        self.D = index.documentWords
        self.d_avg = np.mean(list(self.D.values()))
        self.totalDocs = N
        self.k=k
        self.b=b
    def getTDmatrix(self,query):
        #print(self.d_avg)
        TD={}
        for word in query:
            print(word)
            for doc,frequency in self.index.invertedindex[word]:
                TD[(word,doc)] = frequency
        return TD
    def getIDF(self,query,TD):
        IDF={}
        for q in query:
            Nq=0
            for word,_ in TD.keys():
                if(q==word):
                    Nq+=1
            IDF[q]=log(1+((self.totalDocs-Nq+0.5)/(Nq+0.5)))
        return IDF
    def getTermFrequency(self,query,TD):
        TF = defaultdict(lambda:0)
        for q in query:
            for word,_ in TD.keys():
                print(word)
                if(q==word):
                    TF[q]+=1
        return TF
    def getDocumentsRank(self,query):
        query = word_tokenize(query)
        TD = self.getTDmatrix(query)
        print(TD)
        IDF = self.getIDF(query,TD)
        print(IDF)
        TF = self.getTermFrequency(query,TD)
        print(TF)
        ranks=defaultdict(lambda:0)
        for q in query:
            for word,D in TD.keys():
                if(word==q):
                    numerator = TD[word,D]*(self.k+1)
                    denominator = TF[q]+self.k*(1-self.b+self.b*(self.D[D]/self.d_avg))
                    ranks[D] += IDF[q]*(numerator/denominator)  
        return ranks