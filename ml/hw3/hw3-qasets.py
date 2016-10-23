import numpy as np
import numpy.random as nr

from sklearn.svm import SVC
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score

import itertools
import math
import re
import word2vec

nr.seed(3244)

# load word2vec
w2vModel = word2vec.load('text8.bin')
# w2vModel = word2vec.load('train-100.bin')
w2vDimension = w2vModel.vectors.shape[1]
print('word2vec dimension: ' + str(w2vDimension) + '\n')

# load datasets code
def parseLineTraining(line):
    isQuestion = (line.find("?") != -1)
    line = line.rstrip().split(" ")
    index = line[0]
    line = line[1:]
    words = []
    answerStr = ''
    for x in line:
        tokens = x.split('\t')
        if len(tokens) == 2:
            questionStr = tokens[0]
            answerStr = tokens[1]
            words.append(re.sub(r'[^\w]', '', questionStr))
            # answers = answerStr.split(',')
            # print(words)
            # print(answers)
        else:
            words.append(re.sub(r'[^\w]', '', x))
    return (index, isQuestion, words, answerStr)

dataTrain = []
labelTrain = []

# for testing/debugging purposes only
dataTrainRawFiltered = []
dataTrainRaw = []

def getVectorFromWord(word):
    if word in w2vModel:
        return w2vModel[word]
    else:
        # out of dictionary words have zero weights
        return np.zeros(w2vDimension)

def isFactRelevant(fact, questionWords):
    return len(set.intersection(set(fact), set(questionWords))) > 0

def getRelevantFacts(existingFacts, questionWords):
    relevantFacts = [i for i in existingFacts if isFactRelevant(i, questionWords)]
    # flatten list
    return list(itertools.chain.from_iterable(relevantFacts))

def addTrainingData(questionFacts, questionWords, answers):
    # print(questionFacts)
    # print(questionWords)
    # print(getRelevantFacts(questionFacts, questionWords))
    # print('-------')
    vectorWords = [getVectorFromWord(w) for w in getRelevantFacts(questionFacts, questionWords)]
    dataTrain.append(np.sum(vectorWords, axis=0))
    dataTrainRawFiltered.append(getRelevantFacts(questionFacts, questionWords))
    dataTrainRaw.append(questionFacts)
    labelTrain.append(answers)

def loadTrainingData(f):
    existingFacts = []
    existingFactsWithQuestions = []
    for line in f:
        index, isQuestion, words, answers = parseLineTraining(line)
        if index == '1':
            existingFacts = []
            existingFactsWithQuestions = []
        if isQuestion:
            existingFactsWithQuestions.append(words)
            questionFacts = existingFacts[:]
            questionFacts.append(words)
            addTrainingData(questionFacts, words, answers)
        else:
            existingFactsWithQuestions.append(words)
            existingFacts.append(words)

with open('train.txt', 'r') as f:
# with open('train-s.txt', 'r') as f:
    loadTrainingData(f)

print('train data size: ' + str(len(dataTrain)))
print('--------------------')

# Learning code

def svmCrossValidate(dataTrain, labelTrain, cost, kernel, gamma, degree):
    clf = SVC(cost, kernel, degree, gamma)
    scores = cross_val_score(clf, dataTrain, labelTrain, cv=5)
    print(scores)

def svmTrain(dataTrain, labelTrain, cost, kernel, gamma, degree):
    # print(labelTrain)
    # labelTrain = le.transform(labelTrain)
    # print(labelTrain)
    # clf = SVC(cost, kernel, degree, gamma, class_weight="balanced")
    clf = SVC(cost, kernel, degree, gamma)
    clf.fit(dataTrain, labelTrain)
    return (clf, np.sum(clf.n_support_))

def printWrongPredict(idx, predicted):
    print(dataTrainRaw[idx])
    print(dataTrainRawFiltered[idx])
    print('X: ' + predicted + ' Y: ' + labelTrain[idx])
    print('------')

def svmPredict(dataTrain, labelTrain, svmModel):  
    # labelTrain = le.transform(labelTrain)  
    err_sum = 0
    predicted = svmModel.predict(dataTrain)
    N = len(predicted)
    for idx in range(N):
        if predicted[idx] != labelTrain[idx]:
            err_sum += 1
            printWrongPredict(idx, predicted[idx])
    err_ave = (1 / N) * err_sum
    return 1 - err_ave

# Evaluation

def parseLineTesting(line):
    isQuestion = (line.find("?") != -1)
    line = line.rstrip().split(" ")
    index = line[0]
    line = line[1:]
    words = []
    answerStr = ''
    for x in line:
        words.append(re.sub(r'[^\w]', '', x))
    return (index, isQuestion, words)

def getSvmOutput(questionFacts, existingFactsWithQuestions, questionWords, svmModel):
    vectorWords = [getVectorFromWord(w) for w in getRelevantFacts(questionFacts, questionWords)]
    # flatten existing facts list
    flattenedExistingFacts = list(itertools.chain.from_iterable(existingFactsWithQuestions))
    answerStr = svmModel.predict(np.sum(vectorWords, axis=0).reshape(1,-1))
    # print(answerStr)
    answers = answerStr[0].split(',')
    if len(answers) == 1:
        answer = answers[0]
        if answer == 'nothing':
            return str(-1)
        elif answer in flattenedExistingFacts:
            # print(answer + '\n')
            # print(flattenedExistingFacts)
            # print('\n')
            return str(flattenedExistingFacts.index(answer) + 1)
        else:
            # print('cannot find predicted word ' + answer + ' in facts:\n')
            # print(flattenedExistingFacts)
            # print('\n')
            return str(-1)
    else:
        indices = []
        for answer in answers:
            if answer in flattenedExistingFacts:
                indices.append(flattenedExistingFacts.index(answer) + 1)
        return " ".join(str(x) for x in sorted(indices))

def printOutput(fo, storyId, questionId, output):
    fo.write(str(storyId) + '_' + str(questionId) + ',' + output + '\n')

def svmTest(f, svmModel):
    fo = open('test-output-' + kernel + '-filter.txt', 'w')
    fo.write("textID,sortedAnswerList" + '\n')
    existingFacts = []
    existingFactsWithQuestions = []
    storyId = 0
    questionId = 1
    for line in f:
        index, isQuestion, words = parseLineTesting(line)
        if index == '1':
            storyId += 1
            questionId = 1
            existingFacts = []
            existingFactsWithQuestions = []
        if isQuestion:
            existingFactsWithQuestions.append(words)
            questionFacts = existingFacts[:]
            questionFacts.append(words)
            output = getSvmOutput(questionFacts, existingFactsWithQuestions, words, svmModel)
            # if storyId == 1 and questionId == 1:
            #     print(existingFacts)
            printOutput(fo, storyId, questionId, output)
            questionId += 1
        else:
            existingFactsWithQuestions.append(words)
            existingFacts.append(words)    

# printing util function
def printResult(kernel, cost, totalSV, trainAccuracy, testAccuracy):
    print("Kernel: "+ str(kernel)+"\n")
    print("Cost: "+ str(cost)+ "\n")
    print("Number of Support Vectors: "+ str(totalSV)+"\n")
    print("Train Accuracy: "+ str(trainAccuracy)+"\n")
    print("Test Accuracy: " + str(testAccuracy)+"\n")

cost = 1
kernel='rbf'
# kernel = 'poly'
degree = 3
gamma = 'auto'

# train your svm
# svmModel, totalSV = svmTrain(dataTrain, labelTrain, cost, kernel, gamma, degree)

# test on the training data
# trainAccuracy = svmPredict(dataTrain, labelTrain, svmModel)

# test on your test data
# testAccuracy = 0

# printResult(kernel, cost, totalSV, trainAccuracy, testAccuracy)

svmCrossValidate(dataTrain, labelTrain, cost, kernel, gamma, degree)

# with open('test.txt', 'r') as fTest:
#     svmTest(fTest, svmModel)
