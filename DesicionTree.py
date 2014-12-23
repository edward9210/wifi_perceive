from math import log
import operator

class DecisionTree:
    def __init__(self, dataSet, labels, labelsDict):
        self.dataSet = dataSet
        self.labels = labels
        self.labelsDict = labelsDict
        self.tree = self.createTree(dataSet, labels)

    def calcShannonEnt(self, dataSet):
        numEntries = len(dataSet)
        labelCounts = {}
        for featVec in dataSet:
            currentLabel = featVec[-1]
            if currentLabel not in labelCounts.keys():
                labelCounts[currentLabel] = 0
            labelCounts[currentLabel] += 1
        shannonEnt = 0.0
        for key in labelCounts:
            prob = float(labelCounts[key])/numEntries
            shannonEnt -= prob * log(prob, 2.0)
        return shannonEnt

    def splitDataSet(self, dataSet, axis, value):
        retDataSet = []
        for featVec in dataSet:
            if featVec[axis] == value:
                reduceFeatVec = featVec[:axis]
                reduceFeatVec.extend(featVec[axis + 1:])
                retDataSet.append(reduceFeatVec)
        return retDataSet

    def chooseBestFeatureToSplit(self, dataSet):
        numFeatures = len(dataSet[0]) - 1
        baseEntropy = self.calcShannonEnt(dataSet)
        bestInfoGain = 0.0
        bestFeature = -1
        for i in range(numFeatures):
            featList = [example[i] for example in dataSet]
            uniqueVals = set(featList)
            newEntropy = 0.0
            for value in uniqueVals:
                subDataSet = self.splitDataSet(dataSet, i, value)
                prob = len(subDataSet) / float(len(dataSet))
                newEntropy += prob * self.calcShannonEnt(subDataSet)
            infoGain = baseEntropy - newEntropy
            if infoGain > bestInfoGain:
                bestInfoGain = infoGain
                bestFeature = i
        return bestFeature

    def majorityCnt(self, classList):
        classCount = {}
        for vote in classList:
            if vote not in classCount.keys():
                classCount[vote] = 0
            classCount[vote] += 1
        sortedClassCount = sorted(classCount.iteritems(), key = operator.itemgetter(1), reverse=True)
        return sortedClassCount[0][0]

    def createTree(self, dataSet, labels):
        classList = [example[-1] for example in dataSet]
        if classList.count(classList[0]) == len(classList):
            return classList[0]
        if len(dataSet[0]) == 1:
            return self.majorityCnt(classList)
        bestFeat = self.chooseBestFeatureToSplit(dataSet)
        bestFeatLabel = labels[bestFeat]
        myTree = {bestFeatLabel:{}}
        del(labels[bestFeat])
        featValues = [example[bestFeat] for example in dataSet]
        uniqueVals = set(featValues)
        for value in uniqueVals:
            subLabels = labels[:]
            myTree[bestFeatLabel][value] = self.createTree(self.splitDataSet(dataSet, bestFeat, value), subLabels)
        return myTree

    def getLabel(self, data):
        tree = self.tree
        while True:
            if type(tree) is not dict:
                return tree
            feat = ''
            for key in tree:
                feat = key
            tree = tree[feat]
            value = data[self.labelsDict[feat]]
            flag = 0
            for key in tree:
                if value == key:
                    flag = 1
                    break
            if flag == 0:
                return -1
            else:
                tree = tree[value]



    @property
    def dtree(self):
        return self.tree

