#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from WCM.db import get_db
from PAM.decisionTreeC4_5 import predict

class Test:
    """
        Test Model
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
        self.__resultList = self.__db.result.find()
        self.__resultDict = {}
        for result in self.__resultList:
            self.__resultDict[result['name']] = {
                'trees' : result['trees']
            }

    @property
    def dataNameList(self):
        """
            get data name list
        """
        return sorted(self.__dataDict.keys())

    @property
    def resultNameList(self):
        """
            get result name list
        """
        return sorted(self.__resultDict.keys())

class TestResult:
    """
        Test Result Model
    """
    def __init__(self, data_name, test_name):
        self.__data_name = data_name
        self.__test_name = test_name
        self.__correct_rate = 0.0
        self.__test_data = []
        self.__trees = []
        self.__type = None
        self.__error_data = []
        self.__test()

    def __test(self):
        db = get_db()
        dataList = db.sampledata.find()
        for data in dataList:
            if data['name'] == self.__data_name:
                self.__test_data = data['data']
                self.__type = data['type']
                break
        resultList = db.result.find()
        for result in resultList:
            if result['name'] == self.__test_name:
                self.__trees = result['trees']
                break
        count = 0
        for data in self.__test_data:
            vote = {}
            for tree in self.__trees:
                label = predict(tree, data)
                if label not in vote.keys():
                    vote[label] = 0
                vote[label] += 1
            max = 0
            majorityLabel = None
            for label in vote.keys():
                if vote[label] > max:
                    max = vote[label]
                    majorityLabel = label
            if majorityLabel == self.__type:
                count += 1
            else:
                self.__error_data.append(data)
        self.__correct_rate = float(count) / len(self.__test_data)
        # print self.__correct_rate

    @property
    def correctRate(self):
        return self.__correct_rate

    @property
    def numOfTest(self):
        return len(self.__test_data)

    @property
    def errorData(self):
        return self.__error_data


