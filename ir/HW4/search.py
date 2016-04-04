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

# nonDescriptiveTerms = ['Relevant', 'documents', 'will', 'describe']
nonDescriptiveTerms = []

totalDocuments = 0
maxDocID = 0

RELEVANT_SCORE_THRESHOLD = 0.09
QUERY_TITLE_WEIGHT = 1.0
QUERY_DESCRIPTION_WEIGHT = 1.0

def parseQueryXML(query_file):
    tree = ET.parse(query_file)
    root = tree.getroot()
    title = stripPunctuationAndNonAscii(root.find('title').text)
    description = stripPunctuationAndNonAscii(root.find('description').text)
    titleTerms = [normalizeToken(j) for j in title.split()]
    descriptionTerms = [normalizeToken(j) for j in description.split()]
    # print(titleTerms)
    # print(descriptionTerms)
    return [titleTerms, descriptionTerms]

def getQueryWeight(term, query):
        # return 0
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
    if term in nonDescriptiveTerms:
        # print('term: ' + term + '\t tfidf: ' + str(tf * idf))
        # print('Assigning no weight to non-descriptive term ' + term)
        return 0
    return tf * idf
    # return 1.0

def executeQuery(titleTerms, descriptionTerms):
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
        # if 'US7442313' in docIDWithZone:
        #     print(docIDWithZone + ' ' + str(score))
        docID = removeZoneFromID(docIDWithZone)
        # print(score)
        if score != 0 and queryWeightSqSum != 0 and docLengthDict[docID] != 0:
            # normalization of query length
            docScores[docIDWithZone] = score / (math.sqrt(queryWeightSqSum))
            # normalization of document length
            docScores[docIDWithZone] = docScores[docIDWithZone] / docLengthDict[docID]
    # print(docScores)

    result = {}
    resultList = []
    topList = []
    minTopScore = 100
    maxTopScore = 0
    for docIDWithZone, score in docScores.iteritems():
        docID = removeZoneFromID(docIDWithZone)
        if docID in result:
            result[docID] += score
        else:
            result[docID] = score
    
    for docID, score in result.iteritems():
        # if 'US7442313' in docID:
        #     print(docID + ' ' + str(score))
        # print(docID + ' ' + str(score))
        if score > RELEVANT_SCORE_THRESHOLD:
            # print(docID + ' ' + str(score))
            resultList.append(docID)
            if len(topList) < 20:
                topList.append([docID, score])
                if score < minTopScore:
                    minTopScore = score
                if score > maxTopScore:
                    maxTopScore = score
            elif score > minTopScore:
                for entry in topList:
                    if entry[1] == minTopScore:
                        entry[0] = docID
                        entry[1] = score
                        break
                newScores = [entry[1] for entry in topList]
                minTopScore = min(newScores)
                maxTopScore = max(newScores)

    topList = sorted(topList, key=lambda x:x[1], reverse=True)

    resultList = list(set(resultList))
    return [topList, resultList] 

def search():
    global queries_file_q, dictionary_file_d, posting_file_p, output_file, totalDocuments, docLengthDict, nonDescriptiveTerms
    nonDescriptiveTerms = [normalizeToken(t) for t in nonDescriptiveTerms]

    with open(posting_file_p) as postings:
        totalDocuments = int(postings.readline())
        # print("total documents: " + str(totalDocuments))
        # print("------")

    # store dictionary in memory
    with open(dictionary_file_d) as dicts:
        for i, term in enumerate(dicts):
            term, freq = term.strip('\r\n').strip('\n').split(' ')
            dictionary[term] = (i + 1, freq)

    # store document length in memory
    with open(doc_info_file) as docLengths:
        for i, idLengthStr in enumerate(docLengths):
            iD, length = idLengthStr.split()
            docLengthDict[iD] = float(length)

    titleTerms, descriptionTerms = parseQueryXML(queries_file_q)

    topList, resultList = executeQuery(titleTerms, descriptionTerms)

    # print(topList)
    # for entry in topList:
    #     titleList, abstractList, wordsList = parseXML(corpus, docID)

    # print('results: ' + str(len(resultList)))
    resultList = " ".join([str(x) for x in resultList])

    with open(output_file, "w") as o:
        o.write(resultList)
        o.write('\n')
    
def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p posting-file -q file-of-queries"
    + " -o output-file-of-results")

queries_file_i = dictionary_file_d = posting_file_p = output_file = None
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
    # print("--- %s seconds ---" % (time.time() - start_time))
