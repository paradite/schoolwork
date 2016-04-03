#!/use/bin/env python3
from __future__ import division
import os
import sys
import getopt
import glob
import math
import time

import xml.etree.ElementTree as ET

from collections import defaultdict

from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer

from util import *

start_time = time.time()

dictionary = {}
docLengthDict = {};

totalDocuments = 0
maxDocID = 0

RELEVANT_SCORE_THRESHOLD = 0.5
QUERY_TITLE_WEIGHT = 1.0
QUERY_DESCRIPTION_WEIGHT = 0.5

def parseQueryXML(query_file):
    tree = ET.parse(query_file)
    root = tree.getroot()
    title = stripPunctuationAndNonAscii(root.find('title').text)
    description = stripPunctuationAndNonAscii(root.find('description').text)
    titleTerms = [normalizeToken(j) for j in title.split()]
    descriptionTerms = [normalizeToken(j) for j in description.split()]
    print(titleTerms)
    print(descriptionTerms)
    return [titleTerms, descriptionTerms]

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
    global queries_file_q, dictionary_file_d, posting_file_p, output_file, totalDocuments, docLengthDict

    with open(posting_file_p) as postings:
        totalDocuments = int(postings.readline())
        print("total documents: " + str(totalDocuments))

    # store dictionary in memory
    with open(dictionary_file_d) as dicts:
        for i, term in enumerate(dicts):
            term, freq = term.strip('\r\n').strip('\n').split(' ')
            dictionary[term] = (i + 1, freq)

    # store document length in memory
    with open(doc_length_file) as docLengths:
        for i, idLengthStr in enumerate(docLengths):
            iD, length = idLengthStr.split()
            docLengthDict[iD] = float(length)

    titleTerms, descriptionTerms = parseQueryXML(queries_file_q)
    queryWeightSqSum = 0
    docScores = {}
    for term in titleTerms:
        # print(term)
        if not term in dictionary:
            continue
        queryWeight = getQueryWeight(term, titleTerms)
        queryWeightSqSum += queryWeight ** 2
        postings = getPostingList(int(dictionary[term][0]), posting_file_p)
        for doc in postings:
            docIDWithZone, rawtf = doc.split(',')[0], int(doc.split(',')[1])
            docWeight = getDocWeight(rawtf)
            if docIDWithZone in docScores:
                docScores[docIDWithZone] += docWeight * queryWeight * QUERY_TITLE_WEIGHT
            else:
                docScores[docIDWithZone] = docWeight * queryWeight * QUERY_TITLE_WEIGHT

    for term in descriptionTerms:
        # print(term)
        if not term in dictionary:
            continue
        queryWeight = getQueryWeight(term, descriptionTerms)
        queryWeightSqSum += queryWeight ** 2
        postings = getPostingList(int(dictionary[term][0]), posting_file_p)
        for doc in postings:
            docIDWithZone, rawtf = doc.split(',')[0], int(doc.split(',')[1])
            docWeight = getDocWeight(rawtf)
            if docIDWithZone in docScores:
                docScores[docIDWithZone] += docWeight * queryWeight * QUERY_DESCRIPTION_WEIGHT
            else:
                docScores[docIDWithZone] = docWeight * queryWeight * QUERY_DESCRIPTION_WEIGHT
            # print(str(docID) + 
            #     " que w: " + "{0:.2f}".format(queryWeight) + 
            #     " score: " + "{0:.2f}".format(docScores[docID]))
    # print(docScores)
    # Normalization using sum of squares
    for docIDWithZone, score in docScores.iteritems():
        if 'US7442313' in docIDWithZone:
            print(docIDWithZone + ' ' + str(score))
        docID = removeZoneFromID(docIDWithZone)
        # print(score)
        if score != 0 and queryWeightSqSum != 0 and docLengthDict[docID] != 0:
            # normalization of query length
            docScores[docIDWithZone] = score / (math.sqrt(queryWeightSqSum))
            # normalization of document length
            # docScores[docIDWithZone] = docScores[docIDWithZone] / docLengthDict[docID]
    # print(docScores)

    result = {}
    resultList = []
    for docIDWithZone, score in docScores.iteritems():
        docID = removeZoneFromID(docIDWithZone)
        if docID in result:
            result[docID] += score
        else:
            result[docID] = score
    
    for docID, score in result.iteritems():
        if 'US7442313' in docID:
            print(docID + ' ' + str(score))
        # print(docID + ' ' + str(score))
        if score > RELEVANT_SCORE_THRESHOLD:
            resultList.append(docID)

    resultList = list(set(resultList))

    print('results: ' + str(len(resultList)))
    resultList = " ".join([str(x) for x in resultList])

    with open(output_file, "w") as o:
        o.write(resultList)
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
