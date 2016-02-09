#!/usr/bin/python
from __future__ import division
import re
import nltk
import sys
import getopt
import os

from math import log
from nltk.util import ngrams

languages = ['indonesian', 'malaysian', 'tamil']

def extract_grams_from_string(string):
    characters = [c for c in string]
    return list(ngrams(characters, 4))

def read_lines_without_newline(filename):
    f = open(filename)
    content = [(x.strip('\r\n')).strip('\n') for x in f.readlines()]
    return content

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and an URL separated by a tab(\t)
    """
    print 'building language models...'
    LM = {}
    # Store all the grams encountered for add-one smoothing later
    AllGrams = {}
    for language in languages:
        LM[language] = {}
    content = read_lines_without_newline(in_file)
    for line in content:
        line_tuple = line.partition(' ')
        lan = line_tuple[0]
        if(lan in LM):
            four_grams = extract_grams_from_string(line_tuple[2])
            # We do not pad the string
            for gram in four_grams:
                # Store the gram into AllGrams
                AllGrams[gram] = True
                # Store the gram into the LM
                if(gram in LM[lan]):
                    LM[lan][gram] += 1
                else:
                    LM[lan][gram] = 1
        else:
            print "error in input format"
            sys.exit(2)

    # Apply add one smoothing
    for gram in AllGrams:
        for language in languages:
            if not gram in LM[language]:
                LM[language][gram] = 1

    # Convert count to probability for each gram
    for language in languages:
        # print language
        total_count = 0
        for gram in LM[language]:
            total_count += LM[language][gram]
        # print total_count
        for gram in LM[language]:
            LM[language][gram] = LM[language][gram] / total_count

    return LM
    
def test_LM(in_file, out_file, LM):
    """
    test the language models on new URLs
    each line of in_file contains an URL
    you should print the most probable label for each URL into out_file
    """
    print "testing language models..."
    # Remove previous output file to avoid appending to existing file
    try:
        os.remove(out_file)
    except OSError:
        pass
    content = read_lines_without_newline(in_file)
    for n, line in enumerate(content):
        print "index " + str(n)
        score = {} 
        four_grams = extract_grams_from_string(line)
        for language in languages:
            print language
            score[language] = 0
            seen = 0
            unseen = 0
            for gram in four_grams:
                if gram in LM[language]:
                    # Convert multiplication to sum of logs
                    score[language] += log(LM[language][gram])
                    # Record if the gram is seen in LM or not
                    seen += 1
                else:
                    unseen += 1
            """
            Other language detection, step 1
            If there are more unseen 'grams' than seen 'grams' in a sentence for
            a particular language, the language will score a zero for that sentence
            """
            if unseen != 0 and seen != 0 and unseen > seen:
                score[language] = 0
        # Determine the language with the highest score
        prediction = score.keys()[0]
        highscore = score[score.keys()[0]]
        for k, v in score.items():
            if v > highscore:
                prediction = k
                highscore = v
        """
        Other language detection, step 2
        If all known languages have a score of zero, then the language is predicted to be 
        from other
        """
        if highscore == 0:
            prediction = 'other'
        # print prediction
        with open(out_file, "a") as myfile:
            myfile.write(prediction + ' ' + line + '\r\n')
def usage():
    print "usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"

input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
