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

# We use the nltk stopwords from http://www.nltk.org/book/ch02.html
stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

# stopwords specific to patents
# stopwords.extend(['method', 'system', 'apparatus'])
stopwords.extend(['one'])
stopwords.extend(['step'])
stopwords.extend(['method'])
stopwords.extend(['apparatus'])
stopwords.extend(['use'])
stopwords.extend(['also'])
stopwords.extend(['first'])
stopwords.extend(['example'])

stopwords = [normalizeToken(word) for word in stopwords]

start_time = time.time()

dictionary = {}
docLengthDict = {};

# Store terms of each patent in memory for convenience since the corpus is small
docTermsDict = {};

totalDocuments = 0
maxDocID = 0

RELEVANT_SCORE_THRESHOLD_INIT = 0.10
TOP_LIST_LENGTH = 40
RELEVANT_SCORE_THRESHOLD_EXPANDED = 1.16
NO_OF_EXPANDED_QUERIES = 100
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
    # print('rawtf: ' + str(rawtf) + ' , tf: ' + str(tf))
    tf = getTf(term, query)
    idf = getIdf(term)
    # print('term: ' + term + ', tf: ' + str(tf) + ' , idf: ' + str(idf))
    return tf * idf
    # return 1.0

def getTf(term, query):
    rawtf = query.count(term)
    tf = 1
    if rawtf > 0:
        tf = 1 + math.log(rawtf, 10)
    return tf

def getIdf(term):
    df = 0
    idf = 0
    if term in dictionary:
        df = int(dictionary[term][1])
        if df > 0:
            idf = math.log(totalDocuments / df, 10)
    return idf

def executeQuery(titleTerms, descriptionTerms, scoreThreshold):
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
        if score > scoreThreshold:
            # print(docID + ' ' + str(score))
            resultList.append(docID)
            if len(topList) < TOP_LIST_LENGTH:
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
    with open(doc_info_file) as docInfos:
        for i, idInfoStr in enumerate(docInfos):
            iD, length, termsStr = idInfoStr.split()
            docLengthDict[iD] = float(length)
            docTermsDict[iD] = termsStr.split(',')

    titleTerms, descriptionTerms = parseQueryXML(queries_file_q)

    topList, resultList = executeQuery(titleTerms, descriptionTerms, RELEVANT_SCORE_THRESHOLD_INIT)

    # print(topList)
    
    # Query expansion using top results from first query
    expandedQuery = []
    for entry in topList:
        docID = entry[0]
        if docID in docTermsDict:
            # print(docTermsDict[docID])
            expandedQuery.extend(docTermsDict[docID])
        else:
            print('document terms not available')
    expandedQuery = sorted(expandedQuery, key=str.lower)
    # print(expandedQuery)
    expandedQuerySet = set(expandedQuery)
    expandedQuerySet = sorted(expandedQuerySet, key=str.lower)
    for i, term in enumerate(expandedQuerySet):
        if not term in dictionary:
            continue
        # We use tf instead of tf-idf for weight of each term because 
        # tf-idf gives higher scores to rare words which are not useful
        queryWeight = getTf(term, expandedQuery)
        # print(queryWeight)
        expandedQuerySet[i] = [term, queryWeight]

    # Using tf alone gives us a lot of stopwords, so we remove them
    # with the help of nltk stopwords
    expandedQuerySet = [t for t in expandedQuerySet if t[0] not in stopwords]
    sortedQuery = sorted(expandedQuerySet, key=lambda x:x[1], reverse=True)
    topQuery = [q[0] for q in sortedQuery[:NO_OF_EXPANDED_QUERIES]]
    print(topQuery)
    # Use back the original number of terms instead of using one for each term
    # to better reflect term frequency
    topQueryWithRepeats = [q for q in expandedQuery if q in topQuery]
    # print(topQueryWithRepeats)

    # Execute second round of search using expanded query
    # Expanded queries all have the same the weight as descriptions
    topList, resultList = executeQuery([], topQueryWithRepeats, RELEVANT_SCORE_THRESHOLD_EXPANDED)
    # print(topList)

    print('results: ' + str(len(resultList)))
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
