import numpy as np
import numpy.random as nr

from sklearn.svm import SVC
from sklearn import preprocessing

import math
import re
import word2vec

nr.seed(3244)

# load word2vec
w2vDimension = 100
w2vModel = word2vec.load('text8.bin')

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

def getVectorFromWord(word):
    if word in w2vModel:
        return w2vModel[word]
    else:
        # out of dictionary words have zero weights
        return np.zeros(100)

def addTrainingData(existingFacts, answers):
    vectorWords = [getVectorFromWord(w) for w in existingFacts]
    dataTrain.append(np.sum(vectorWords, axis=0))
    labelTrain.append(answers)

def loadTrainingData(f):
    existingFacts = []
    for line in f:
        index, isQuestion, words, answers = parseLineTraining(line)
        if index == '1':
            existingFacts = []
        elif isQuestion:
            existingFacts.extend(words)
            addTrainingData(existingFacts, answers)
        else:
            existingFacts.extend(words)

with open('train.txt', 'r') as f:
# with open('train-s.txt', 'r') as f:
    loadTrainingData(f)

print('train data size: ' + str(len(dataTrain)))
print('--------------------')

# Learning code
def svmTrain(dataTrain, labelTrain, cost, kernel, gamma, degree):
    # print(labelTrain)
    # labelTrain = le.transform(labelTrain)
    # print(labelTrain)
    clf = SVC(cost, kernel, degree, gamma)
    clf.fit(dataTrain, labelTrain)
    return (clf, np.sum(clf.n_support_))

def svmPredict(dataTrain, labelTrain, svmModel):  
    # labelTrain = le.transform(labelTrain)  
    err_sum = 0
    predicted = svmModel.predict(dataTrain)
    N = len(predicted)
    for idx in range(N):
        if predicted[idx] != labelTrain[idx]:
            err_sum += 1
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

def getSvmOutput(existingFacts, svmModel):
    vectorWords = [getVectorFromWord(w) for w in existingFacts]
    answerStr = svmModel.predict(np.sum(vectorWords, axis=0).reshape(1,-1))
    # print(answerStr)
    answers = answerStr[0].split(',')
    if len(answers) == 1:
        answer = answers[0]
        if answer == 'nothing':
            return str(-1)
        elif answer in existingFacts:
            # print(answer + '\n')
            # print(existingFacts)
            # print('\n')
            return str(existingFacts.index(answer) + 1)
        else:
            # print('cannot find predicted word ' + answer + ' in facts:\n')
            # print(existingFacts)
            # print('\n')
            return str(-1)
    else:
        indices = []
        for answer in answers:
            if answer in existingFacts:
                indices.append(existingFacts.index(answer) + 1)
        return " ".join(str(x) for x in sorted(indices))

def printOutput(fo, storyId, questionId, output):
    fo.write(str(storyId) + '_' + str(questionId) + ',' + output + '\n')

def svmTest(f, svmModel):
    fo = open('test-output.txt', 'w')
    fo.write("textID,sortedAnswerList" + '\n')
    existingFacts = []
    storyId = 0
    questionId = 1
    for line in f:
        index, isQuestion, words = parseLineTesting(line)
        if index == '1':
            storyId += 1
            questionId = 1
            existingFacts = []
        if isQuestion:
            existingFacts.extend(words)
            output = getSvmOutput(existingFacts, svmModel)
            # if storyId == 1 and questionId == 1:
            #     print(existingFacts)
            printOutput(fo, storyId, questionId, output)
            questionId += 1
        else:
            existingFacts.extend(words)    

# printing util function
def printResult(kernel, cost, totalSV, trainAccuracy, testAccuracy):
    print("Kernel: "+ str(kernel)+"\n")
    print("Cost: "+ str(cost)+ "\n")
    print("Number of Support Vectors: "+ str(totalSV)+"\n")
    print("Train Accuracy: "+ str(trainAccuracy)+"\n")
    print("Test Accuracy: " + str(testAccuracy)+"\n")

cost = 1
kernel = 'poly'
degree = 3
gamma = 'auto'

# train your svm
svmModel, totalSV = svmTrain(dataTrain, labelTrain, cost, kernel, gamma, degree)

# test on the training data
trainAccuracy = svmPredict(dataTrain, labelTrain, svmModel)

# test on your test data
testAccuracy = 0

printResult(kernel, cost, totalSV, trainAccuracy, testAccuracy)

with open('test.txt', 'r') as fTest:
    svmTest(fTest, svmModel)
