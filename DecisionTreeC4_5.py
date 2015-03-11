from math import log
import operator


class DecisionTreeC4_5:
    def __init__(self, dataSet, attrNamelist, attrNameDict):
        """
            init the decision tree
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

    def __calcEntropy(self, dataSet):
        """
            calculate the Entropy for the given dataSet.
            :param dataSet: [[attrValue1, attrValue2, ..., label], [], []]
            :return entropy: a float value between 0 - 1
        """
        numOfEntries = len(dataSet)
        labelCounts = {}
        for data in dataSet:
            label = data[-1]
            if label not in labelCounts.keys():
                labelCounts[label] = 0
            labelCounts[label] += 1
        entropy = 0.0
        for key in labelCounts:
            prob = float(labelCounts[key]) / numOfEntries
            entropy -= prob * log(prob, 2.0)
        return entropy

    def __calcGainRatio(self, dataSet, axis):
        """
            calculate the the information gain ratio for the given dataSet
            :param dataSet: [[attrValue1, attrValue2, ..., label], [], []]
            :param axis: the sequence num of attribute in dataSet
            :return: (split point, Gain Ratio) : a tuple for split point and the Gain Ratio for dataSet
        """
        baseEntropy = self.__calcEntropy(dataSet)
        allValInSelectedAttr = list(set([(example[axis], example[-1]) for example in dataSet]))
        allValInSelectedAttr.sort()
        # print allValInSelectedAttr
        splitPoints = []
        preRssi = allValInSelectedAttr[0][0]
        preLabel = allValInSelectedAttr[0][1]
        for rssi, label in allValInSelectedAttr:
            if preLabel != label:
                splitPoints.append(float(rssi + preRssi) / 2.0)
            preRssi = rssi
            preLabel = label
        # print splitPoints
        bestInfoGainRatio = 0.0
        bestSpiltPoint = 0.0
        numOfEntries = len(dataSet)
        for sp in splitPoints:
            smallerDataSet, largerDataSet = self.__splitDataSet(dataSet, axis, sp)
            if len(smallerDataSet) == 0 or len(largerDataSet) == 0:
                continue
            prob = float(len(smallerDataSet)) / float(numOfEntries)
            newEntropy = prob * self.__calcEntropy(smallerDataSet) + (1 - prob) * self.__calcEntropy(largerDataSet)
            infoGain = baseEntropy - newEntropy
            splitInfo = -(prob * log(prob, 2.0) + (1 - prob) * log((1 - prob), 2.0))
            infoGainRatio = infoGain / splitInfo
            # print sp, infoGainRatio
            if infoGainRatio > bestInfoGainRatio:
                bestInfoGainRatio = infoGainRatio
                bestSpiltPoint = sp
        # print bestInfoGainRatio, bestSpiltPoint
        return bestSpiltPoint, bestInfoGainRatio

    def __splitDataSet(self, dataSet, axis, splitPoint):
        """
            split dataSet by splitPoint
            :param dataSet: [[attrValue1, attrValue2, ..., label], [], []]
            :param axis: the sequence num of attribute in dataSet
            :param splitPoint: the value of split point
            :return: two splited dataSet by splitPoint : smaller than splitPoint's dataSet and larger than splitPoint's dataSet
        """
        splitSmallDataSet = []
        splitLargeDataSet = []
        for data in dataSet:
            dataVec = data[:axis]
            dataVec.extend(data[axis + 1 :])
            if data[axis] < splitPoint:
                splitSmallDataSet.append(dataVec)
            else:
                splitLargeDataSet.append(dataVec)
        return splitSmallDataSet, splitLargeDataSet

    def __chooseBestAttribute(self, dataSet):
        """
            calculate the information gain ratio and choose the best attribute to split the given dataSet.
            :param dataSet: [[attrValue1, attrValue2, ..., label], [], []]
            :return bestAttr, bestSplitPoint: best attribute(the sequence num of the attribute) and bestSplitPoint(a float value)
        """
        numOfAttrs = len(dataSet[0]) - 1
        bestInfoGainRatio = 0.0
        bestAttr = -1
        bestSplitPoint = 0.0
        for i in range(numOfAttrs):
            splitPoint, gainRatio = self.__calcGainRatio(dataSet, i)
            if gainRatio > bestInfoGainRatio:
                bestInfoGainRatio = gainRatio
                bestAttr = i
                bestSplitPoint= splitPoint
        return bestAttr, bestSplitPoint

    def __majorityCount(self, labelList):
        """
            count the majority label in the label list
            :param labelList: a list of labels
            :return: majority of label
        """
        labelCount = {}
        for vote in labelList:
            if vote not in labelCount.keys():
                labelCount[vote] = 0
            labelCount[vote] += 1
        sortedLabelCount = sorted(labelCount.iteritems(), key = operator.itemgetter(1), reverse = True)
        return sortedLabelCount[0][0]

    def __createTree(self, dataSet, attrNamelist):
        """
            create the decision tree by C4_5 algorithm
            :param dataSet: [[attrValue1, attrValue2, ..., label], [], []]
            :param attrNamelist: attributes' names list
            :return: the decision tree for the given dataSet
        """
        labelList = [data[-1] for data in dataSet]
        if labelList.count(labelList[0]) == len(labelList):
            return labelList[0]
        if len(dataSet[0]) == 1:
            return self.__majorityCount(labelList)
        bestAttr, bestSplitPoint = self.__chooseBestAttribute(dataSet)
        bestAttrName = attrNamelist[bestAttr]
        myTree = {(bestAttrName, bestSplitPoint) : {}}
        del(attrNamelist[bestAttr])
        leftChildDataSet, rightChildDataSet = self.__splitDataSet(dataSet, bestAttr, bestSplitPoint)
        if len(leftChildDataSet) != 0:
            myTree[(bestAttrName, bestSplitPoint)]['left'] = self.__createTree(leftChildDataSet, attrNamelist[:])
        if len(rightChildDataSet) != 0:
            myTree[(bestAttrName, bestSplitPoint)]['right'] = self.__createTree(rightChildDataSet, attrNamelist[:])
        return myTree

    def createTree(self):
        """
            create the decision tree by C4_5 algorithm
            :return: the decision tree constructed by C4_5 algorithm
        """
        self.__tree = self.__createTree(self.__dataSet, self.__attrNamelist)
        return self.__tree

    def getLabel(self, dataVec):
        """
            get the label prediction for the input dataVec
            :param dataVec: [attrValue1, attrValue2, ...]
            :return: the label prediction
        """
        tree = self.__tree
        while True:
            if type(tree) is not dict:
                return tree
            attrName, splitPoint = tree.keys()[0]
            tree = tree[(attrName, splitPoint)]
            value = dataVec[self.__attrNameDict[attrName]]
            if value < splitPoint:
                tree = tree['left']
            else:
                tree = tree['right']





