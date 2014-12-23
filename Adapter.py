from __future__ import print_function
import re

NULL_RSSI_VALUE = -128

class Adapter:
    def __init__(self, filepath):
        self.filepath = filepath
        self.ap_dict = {}
        self.ap_list = []
        self.data_set = []
        self.__bulidApMap()
        self.__transfromDataToInputForm()

    def __bulidApMap(self):
        file = open(self.filepath, 'r')
        self.ap_dict = {}
        self.ap_list = []
        while True:
            linetext = file.readline()
            if not linetext:
                break
            split_result = re.split(r',', linetext)
            for i in range(len(split_result) - 1):
                mac = re.split(r':-', split_result[i])[0]
                if mac not in self.ap_dict:
                    self.ap_dict[mac] = 0
                    self.ap_list.append(mac)
        self.ap_list.sort()
        count = 0
        for i in range(len(self.ap_list)):
            self.ap_dict[self.ap_list[i]] = count
            count += 1
        print (self.ap_dict)

    def __transfromDataToInputForm(self):
        self.data_set = []
        file = open(self.filepath, 'r')
        while True:
            linetext = file.readline()
            if not linetext:
                break
            split_result = re.split(r',', linetext)
            dict = {}
            for i in range(len(split_result) - 1):
                res = re.split(r':-', split_result[i])
                mac = res[0]
                rssi = -int(res[1])
                dict[mac] = rssi
                # print(mac + ' : ' + str(rssi))
            area_type = int(re.split(r'\r\n', split_result[len(split_result) - 1])[0])
            # print(area_type)
            tmp_list = []
            for i in range(len(self.ap_list)):
                if self.ap_list[i] not in dict:
                    tmp_list.append(NULL_RSSI_VALUE)
                else:
                    tmp_list.append(dict[self.ap_list[i]])
            tmp_list.append(area_type)
            self.data_set.append(tmp_list)
        print(self.data_set)

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


