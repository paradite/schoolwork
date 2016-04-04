#!/use/bin/env python3
from __future__ import division
import os
import sys
import getopt
import glob
import math

from util import *

def check():
    resultList = []
    positiveNo = 0
    negativeNo = 0
    totalPositiveNo = 0
    totalNegativeNo = 0
    global positive_file, negative_file, result_file

    with open(result_file) as results:
        for result in results:
            resultList = result.split()
            # print(resultList)

    with open(positive_file) as positiveList:
        for pos in positiveList:
            pos = pos.strip('\r\n').strip('\n')
            totalPositiveNo += 1
            if pos in resultList:
                positiveNo += 1

    with open(negative_file) as negativeList:
        for neg in negativeList:
            neg = neg.strip('\r\n').strip('\n')
            totalNegativeNo += 1
            if neg in resultList:
                negativeNo += 1
    print("------")
    # print(result_file)
    # print('positive: ' + str(positiveNo) + '/' + str(totalPositiveNo))
    # print('negative: ' + str(negativeNo) + '/' + str(totalNegativeNo))
    if len(resultList) == 0:
        precision = 0
    else:
        precision = positiveNo / len(resultList)
    if totalPositiveNo == 0:
        recall = 0
    else:
        recall = positiveNo / totalPositiveNo
    if recall == 0 and precision == 0:
        f2 = 0
    else:
        f2 = (5 * precision * recall)/(4 * precision + recall)
    print('precision: ' + str(precision) + '\trecall: ' + str(recall))
    print('F2: ' + str(f2))
    
def usage():
    print("usage: " + sys.argv[0] + " -p positive-file -n negative-file -r result-file")

positive_file = negative_file = result_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:n:r:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-p':
        positive_file = a
    elif o == '-n':
        negative_file = a
    elif o == '-r':
        result_file = a
    else:
        print(o)
        print(a)
        assert False, "unhandled option"
if positive_file == None or negative_file == None or result_file == None:
    usage()
    sys.exit(2)

if __name__ == "__main__":
    check()
