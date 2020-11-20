from ranking import BM25Ranker
import pickle
from inverted_index import Index
pickle_in = open("index.pkl","rb")
indexobj= pickle.load(pickle_in)
print(indexobj.invertedindex)
query = input("Enter the query:")
ranker = BM25Ranker(indexobj,indexobj.noOfDocuments,1.5,0.75)
documentsRank = ranker.getDocumentsRank(query)
for docID in documentsRank.keys():
    print(indexobj.documents[docID],documentsRank[docID])

