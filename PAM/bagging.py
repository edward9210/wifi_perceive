import random

from decisionTreeC4_5 import DecisionTreeC4_5

class Bagging:
    def __init__(self, dataSet, attrNamelist, attrNameDict):
        """
            init the bagging
            :param dataSet: [[attrValue1, attrValue2, ..., label], [], []]
            :param attrNamelist: [attrName1, attrName2, ...] (like ['d4:ee:07:04:7f:4a', 'd4:ee:07:04:80:88'])
            :param attrNameDict: {attrName1: 0, attrName2: 1, ...} (like {'d4:ee:07:04:7f:4a': 0, 'd4:ee:07:04:80:88': 1})
            :return:
        """
        self.__dataSet = dataSet
        self.__attrNamelist = []
        for attrName in attrNamelist:
            self.__attrNamelist.append(attrName)
        self.__attrNameDict = attrNameDict
        self.__classifiers = None

    def buildTrees(self, numOfTrees = 10, percentage = 0.8):
        """
            using bagging to build decision trees
            :param numOfTrees: the num of decision tree
            :param percentage: the percentage of the training set
            :return:
        """
        numOfEntries = len(self.__dataSet)
        numOfSamples = int(numOfEntries * percentage)
        self.__classifiers = []
        for i in range(numOfTrees):
            trainingSet = []
            for j in range(numOfSamples):
                index = random.randint(0, numOfEntries - 1)
                trainingSet.append(self.__dataSet[index])
            dt = DecisionTreeC4_5(trainingSet, self.__attrNamelist, self.__attrNameDict)
            self.__classifiers.append(dt)
        for i in range(numOfTrees):
            print self.__classifiers[i].dTree

    def predict(self, dataVec):
        """
            get the label prediction for the input dataVec
            :param dataVec: [attrValue1, attrValue2, ...]
            :return: the label prediction
        """
        if self.__classifiers == None:
            self.buildTrees()
        labelConut = {}
        for dt in self.__classifiers:
            vote = dt.predict(dataVec)
            if vote not in labelConut.keys():
                labelConut[vote] = 0
            labelConut[vote] += 1
        bestLabel = -1
        maxCount = 0
        for key in labelConut.keys():
            if labelConut[key] > maxCount:
                maxCount = labelConut[key]
                bestLabel = key
        return bestLabel
