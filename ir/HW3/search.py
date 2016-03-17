#!/use/bin/env python3
from __future__ import division
import os
import sys
import getopt
import glob
import math
import time

from collections import defaultdict

from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus.reader.plaintext import PlaintextCorpusReader

from util import *

start_time = time.time()

dictionary = {}
docLengthList = [];

totalDocuments = 0
maxDocID = 0

def parse_query(query):
    return [normalize_token(t) for t in query.split(' ')]

def getQueryWeight(term, query):
    # print('for term ' + term + ' in query ' + str(query))
    rawtf = query.count(term)
    tf = 1
    if rawtf > 0:
        tf = 1 + math.log(rawtf, 10)
    # print('rawtf: ' + str(rawtf) + ' , tf: ' + str(tf))
    df = 0
    idf = 0
    if term in dictionary:
        df = int(dictionary[term][1])
        if df > 0:
            idf = math.log(totalDocuments / df, 10)
    # print('df: ' + str(df) + ' , idf: ' + str(idf))
    # print('tfidf: ' + str(tf * idf))
    return tf * idf

def search():
    stemmer = PorterStemmer()
    global queries_file_q, dictionary_file_d, posting_file_p, output_file, totalDocuments, maxDocID, docLengthList

    with open(posting_file_p) as postings:
        totalDocuments, maxDocID = [int(x) for x in postings.readline().split(' ')]
        print("total documents: " + str(totalDocuments))
        print("maxDocID: " + str(maxDocID))

    results = []

    # store dictionary in memory
    with open(dictionary_file_d) as dicts:
        for i, term in enumerate(dicts):
            term, freq = term.strip('\r\n').strip('\n').split(' ')
            dictionary[term] = (i + 1, freq)

    # store document length in memory
    with open(doc_length_file) as docLengths:
        docLengthList = [0] * (maxDocID + 1)
        for i, length in enumerate(docLengths):
            docLengthList[i] = float(length)

    with open(queries_file_q) as queries:
        for query in queries:
            print('==============')
            terms = parse_query(query.strip('\r\n').strip('\n'))
            queryWeightSqSum = 0
            docScores = [0] * (maxDocID + 1)
            for term in terms:
                print(term)
                if not term in dictionary:
                    continue
                queryWeight = getQueryWeight(term, terms)
                queryWeightSqSum += queryWeight ** 2
                postings = get_posting_list(int(dictionary[term][0]), posting_file_p)
                for doc in postings:
                    docID, rawtf = [int(i) for i in doc.split(',')]
                    docWeight = getDocWeight(rawtf)
                    docScores[docID] += docWeight * queryWeight
                    # print(str(docID) + 
                    #     " que w: " + "{0:.2f}".format(queryWeight) + 
                    #     " score: " + "{0:.2f}".format(docScores[docID]))
            # print(docScores)
            # Normalization using sum of squares
            for i, score in enumerate(docScores):
                if score != 0 and queryWeightSqSum != 0 and docLengthList[i] != 0:
                    # normalization of query length
                    docScores[i] = score / (math.sqrt(queryWeightSqSum))
                    # normalization of document length
                    docScores[i] = docScores[i] / docLengthList[i]
            # print(docScores)
            # http://stackoverflow.com/questions/6422700/how-to-get-indices-of-a-sorted-array-in-python
            result = [i[0] for i in sorted(enumerate(docScores), key=lambda x:x[1], reverse=True)]
            # remove non-existent document 0
            result.remove(0)
            result = result[:10]
            # remove documents that have score zero
            result[:] = [x for x in result if not docScores[x] == 0]
            results.append(" ".join([str(x) for x in result]))
            print('result length: ' + str(len(result)))
            print(" ".join([str(x) for x in result]))

    with open(output_file, "w") as o:
        o.write('\n'.join(results))
        o.write('\n')
    
def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p posting-file -q file-of-queries"
    + " -o output-file-of-results")

queries_file_i = dictionary_file_d = posting_file_p = output_file = None
doc_length_file = "doclength.txt"
try:
    opts, args = getopt.getopt(sys.argv[1:], 'q:d:p:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-q':
        queries_file_q = a
    elif o == '-d':
        dictionary_file_d = a
    elif o == '-p':
        posting_file_p = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if output_file == None or dictionary_file_d == None or posting_file_p == None or queries_file_q == None:
    usage()
    sys.exit(2)

if __name__ == "__main__":
    search()
    print("--- %s seconds ---" % (time.time() - start_time))
