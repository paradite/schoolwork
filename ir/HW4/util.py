#!/use/bin/env python3
import os
import glob
import math
import string
from itertools import islice

from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import XMLCorpusReader

doc_info_file = "docinfo.txt"
stemmer = PorterStemmer()

def parseXML(corpus, docID):
    xmlNodeList = [j for j in corpus.xml(docID)]
    title = ''
    abstract = ''
    for node in xmlNodeList:
        field = node.attrib.get('name')
        if(field == 'Title'):
            title = stripPunctuationAndNonAscii(node.text)
        if(field == 'Abstract'):
            abstract = stripPunctuationAndNonAscii(node.text)
    print('title', title, 'abstract', abstract)
    titleList = [normalizeToken(j) for j in title.split()]
    abstractList = [normalizeToken(j) for j in abstract.split()]
    wordsList = titleList + abstractList
    return [titleList, abstractList, wordsList]

def removeZoneFromID(id):
    return id[:-4]

def addZoneToID(id, zone):
    return id + '.' + zone[0:3].upper()

def stripPunctuationAndNonAscii(s):
    s = s.strip().encode('ascii', 'ignore')
    return s.translate(string.maketrans("",""), string.punctuation)

def getDocWeight(rawtf):
    tf = 1
    if rawtf > 0:
        tf = 1 + math.log(rawtf, 10)
    # print('rawtf: ' + str(rawtf) + ' , tf: ' + str(tf))
    idf = 1
    # print('tfidf: ' + str(tf * idf))
    return tf * idf

def createCorpusXML(filedir):
    ''' Creates a corpus from xml file'''
    return XMLCorpusReader(filedir, ".*")

def getDocIds(filedir):
    return sorted(os.listdir(filedir), key=lambda x: x)

def normalizeToken(token):
    # Converts unicode string to regular string
    return str(stemmer.stem(token.lower()))

''' Input/Output '''
def listToString(target_list, delimiter=','):
    ''' Generates delimiter i.e ',' separated string'''
    return delimiter.join(target_list)

def writeToFile(filepath, content):
    with open(filepath, 'w') as output:
        output.write(content)

''' Posting list '''
def getPostingList(index, filepath):
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
