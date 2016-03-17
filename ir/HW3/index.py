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

def generate_word_dict_and_doc_length(filedir):
    ''' Generates dictionary of posting list and doc lengths'''
    corpus = create_corpus(filedir)
    doc_ids = get_doc_ids(filedir)
    docLengthList = [0] * (int(doc_ids[len(doc_ids) - 1]) + 1)
    word_dict = defaultdict(list)
    print("Generating word dict and doc lengths")
    for i in doc_ids:
        wordsList = [normalize_token(j) for j in corpus.words(i)]
        words = set(wordsList)
        for word in words:
            word_count = wordsList.count(word)
            word_dict[word].append([i, word_count])
            # Add square of document weight of the term
            docLengthList[int(i)] += getDocWeight(word_count) ** 2
        # square root the sum of squares to get doc length
        docLengthList[int(i)] = math.sqrt(docLengthList[int(i)])
    return [OrderedDict(sorted(word_dict.items())), docLengthList]

def index():
    global input_file_i, dictionary_file_d, posting_file_p

    word_dict, docLengthList = generate_word_dict_and_doc_length(input_file_i)
    with open(dictionary_file_d, "w") as d, open(posting_file_p, "w") as p, open(doc_length_file, "w") as l:
        print("Writing to files")
        # write the number of documents and max docID at first line of the postings file
        docIDs = get_doc_ids(input_file_i)
        p.write(str(len(docIDs)) + " " + docIDs[len(docIDs) - 1] + "\n")
        for k, v in word_dict.items():
            d.write("{} {}\n".format(k, len(v)))
            p.write(" ".join([e[0] + "," + str(e[1]) for e in v]) + "\n")
        for length in docLengthList:
            l.write(str(length) + "\n")

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
