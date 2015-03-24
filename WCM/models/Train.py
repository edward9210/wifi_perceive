#!/usr/bin/env python
# -*- coding: utf-8 -*-

from WCM.db import get_db

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