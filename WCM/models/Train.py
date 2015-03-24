#!/usr/bin/env python
# -*- coding: utf-8 -*-

from WCM.db import get_db
from PAM.adapter import Adapter
from PAM.bagging import Bagging

class Train:
    """
        Train Model
    """
    def __init__(self):
        self.__db = get_db()
        self.__dataList = self.__db.sampledata.find()
        self.__dataDict = {}
        for data in self.__dataList:
            self.__dataDict[data['name']] = {
                'type' : data['type'],
                'data' : data['data'],
                'name' : data['name'],
            }

    @property
    def dataNameList(self):
        return sorted(self.__dataDict.keys())

    def getDataByName(self, name):
        if name in self.__dataDict.keys():
            return self.__dataDict[name]
        else:
            return {
                'type' : None,
                'data' : None,
                'name' : None,
            }

class TrainResult:
    """
        Train Result Model
    """
    def __init__(self, nameList, percentage, treeNum):
        self.__nameList = nameList
        self.__percentage = float(percentage) / 100.0
        self.__treeNum = int(treeNum)
        self.__bagging = None
        self.__correct_rate = 0.0
        self.__train_data = []
        self.__test_data = []

    @property
    def percentage(self):
        return self.__percentage

    @property
    def numOfTree(self):
        return self.__treeNum

    @property
    def correctRate(self):
        return self.__correct_rate

    @property
    def numOfTrain(self):
        return len(self.__train_data)

    @property
    def numOfTest(self):
        return len(self.__test_data)

    @property
    def trees(self):
        return self.__bagging.trees

    def train(self):
        dataSet = []
        for name in self.__nameList:
            data = Train().getDataByName(name)
            data.pop('name')
            dataSet.append(data)
        # print dataSet
        adapter = Adapter(dataSet)
        adapter.disorganizeData()
        spilt_index = int(len(adapter.data) * self.__percentage)
        self.__train_data = adapter.data[: spilt_index]
        self.__test_data = adapter.data[spilt_index :]
        self.__bagging = Bagging(self.__train_data, adapter.apList, adapter.apDict)
        self.__bagging.buildTrees(numOfTrees = self.__treeNum)
        count = 0
        for i in range(0, len(self.__test_data)):
            if self.__test_data[i][-1] == self.__bagging.predict(self.__test_data[i][:-1]):
                count += 1
        # print count
        # print 'correct rate:'
        self.__correct_rate = float(count) / len(self.__test_data)
        # print self.__correct_rate
