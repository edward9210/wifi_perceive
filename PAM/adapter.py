#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

NULL_RSSI_VALUE = -128

class Adapter:
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.ap_dict = {}
        self.ap_list = []
        self.data_set = []
        self.__transfromDataToInputForm()

    def __bulidApMapping(self):
        self.ap_dict = {}
        self.ap_list = []
        for vec in self.__raw_data:
            for data in vec['data']:
                for ap_mac in data.keys():
                    if ap_mac not in self.ap_dict:
                        self.ap_dict[ap_mac] = 0
                        self.ap_list.append(ap_mac)
        self.ap_list.sort()
        count = 0
        for i in range(len(self.ap_list)):
            self.ap_dict[self.ap_list[i]] = count
            count += 1

    def __transfromDataToInputForm(self):
        self.__bulidApMapping()
        self.data_set = []
        for vec in self.__raw_data:
            type = vec['type']
            for data in vec['data']:
                tmp_list = []
                for i in range(len(self.ap_list)):
                    ap_mac = self.ap_list[i]
                    if ap_mac not in data.keys():
                        tmp_list.append(NULL_RSSI_VALUE)
                    else:
                        tmp_list.append(data[ap_mac])
                tmp_list.append(type)
                self.data_set.append(tmp_list)
        # print self.data_set
        # print self.ap_list
        # print self.ap_dict

    def disorganizeData(self):
        newData = []
        numOfEntries = len(self.data_set)
        for i in range(numOfEntries):
            index = random.randint(0, numOfEntries - i - 1)
            newData.append(self.data_set[index])
            del self.data_set[index]
        self.data_set = newData

    @property
    def data(self):
        return self.data_set

    @property
    def apDict(self):
        return self.ap_dict

    @property
    def apList(self):
        return self.ap_list

    def outputCsvFile(self):
        csvFile = open('/Users/edward/Desktop/wifisen/input.csv', 'w')
        for i in range(len(self.ap_list)):
            csvFile.write(self.ap_list[i] + ',')
        csvFile.write('area_type\r\n')
        for i in range(len(self.data)):
            for j in range(len(self.ap_list) + 1):
                csvFile.write(str(self.data[i][j]))
                if j == len(self.ap_list):
                    csvFile.write('\r\n')
                else:
                    csvFile.write(',')


