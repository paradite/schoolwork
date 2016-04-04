#!/use/bin/env python3

import os
import sys
import getopt
import glob
import math
from collections import defaultdict

from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus.reader.plaintext import PlaintextCorpusReader

from util import *
from ordereddict import OrderedDict

def generateWordDictAndDocLength(filedir):
    ''' Generates dictionary of posting list and doc lengths'''
    corpus = createCorpusXML(filedir)
    docIds = getDocIds(filedir)
    docLengthList = [0] * len(docIds)
    wordDict = defaultdict(list)
    print("Generating word dict and doc lengths")
    for i, docID in enumerate(docIds):
        titleList, abstractList, wordsList = parseXML(corpus, docID)
        docID = docID.replace('.xml', '')
        titleSet = set(titleList)
        abstractSet = set(abstractList)
        wordsSet = set(wordsList)
        for word in titleSet:
            wordCount = titleList.count(word)
            wordDict[word].append([addZoneToID(docID, 'Title'), wordCount])
        for word in abstractSet:
            wordCount = wordsList.count(word)
            wordDict[word].append([addZoneToID(docID, 'Abstract'), wordCount])
        for word in wordsSet:
            wordCount = wordsList.count(word)
            # Add square of document weight of the term
            docLengthList[i] += getDocWeight(wordCount) ** 2
        # square root the sum of squares to get doc length
        docLengthList[i] = math.sqrt(docLengthList[i])
        # save the actual doc ID
        docLengthList[i] = [docID, docLengthList[i]]
    return [OrderedDict(sorted(wordDict.items())), docLengthList]

def index():
    global input_file_i, dictionary_file_d, posting_file_p

    wordDict, docLengthList = generateWordDictAndDocLength(input_file_i)
    with open(dictionary_file_d, "w") as d, open(posting_file_p, "w") as p, open(doc_length_file, "w") as l:
        print("Writing to files")
        # write the number of documents at first line of the postings file
        docIDs = getDocIds(input_file_i)
        p.write(str(len(docIDs)) + "\n")
        for k, v in wordDict.items():
            d.write("{} {}\n".format(k, len(v)))
            p.write(" ".join([str(e[0]) + "," + str(e[1]) for e in v]) + "\n")
        for length in docLengthList:
            l.write("{} {}\n".format(str(length[0]), str(length[1])))

def usage():
    print "usage: " + sys.argv[0] + " -i training-input-file -d output-dictionary-file -p output-posting-file"

input_file_i = dictionary_file_d = posting_file_p = None
# File name for generated document lengths
doc_length_file = "doclength.txt"
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        input_file_i = a
    elif o == '-d':
        dictionary_file_d = a
    elif o == '-p':
        posting_file_p = a
    else:
        assert False, "unhandled option"
if input_file_i == None or dictionary_file_d == None or posting_file_p == None:
    usage()
    sys.exit(2)

if __name__ == "__main__":
    index()
