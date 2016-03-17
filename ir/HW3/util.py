#!/use/bin/env python3
import os
import glob
import math
from itertools import islice

from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus.reader.plaintext import PlaintextCorpusReader

stemmer = PorterStemmer()   

def getDocWeight(rawtf):
    tf = 1
    if rawtf > 0:
        tf = 1 + math.log(rawtf, 10)
    # print('rawtf: ' + str(rawtf) + ' , tf: ' + str(tf))
    idf = 1
    # print('tfidf: ' + str(tf * idf))
    return tf * idf

def create_corpus(filedir):
    ''' Creates a corpus based on files that matches the regex in file directory'''
    return PlaintextCorpusReader(filedir, ".*")

def get_doc_ids(filedir):
    return sorted(os.listdir(filedir), key=lambda x: int(x))

def normalize_token(token):
    # Converts unicode string to regular string
    return str(stemmer.stem(token.lower()))

''' Input/Output '''
def list_to_string(target_list, delimiter=','):
    ''' Generates delimiter i.e ',' separated string'''
    return delimiter.join(target_list)

def write_to_file(filepath, content):
    with open(filepath, 'w') as output:
        output.write(content)

''' Posting list '''
def get_posting_list(index, filepath):
    '''Retrieves a posting list given a file handle'''
    with open(filepath) as postings:
        posting_list = []
        try:
            posting_list = next(islice(postings, index, None)).rstrip('\n').rstrip('\r\n').split(' ')
        except StopIteration:
            print("Encounters end of iterator")
        return posting_list
    
if __name__ == "__main__":
    pass
