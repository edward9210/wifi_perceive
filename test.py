from Adapter import Adapter
from DesicionTree import DecisionTree
from DecisionTreeC4_5 import DecisionTreeC4_5

if __name__ == '__main__':
    obj = Adapter('/Users/edward/Desktop/wifi_perceive/data.csv')
    dataSet = obj.data
    ap_list = obj.ap_list
    ap_dict = obj.ap_dict
    # print ap_list, ap_dict
    dt = DecisionTreeC4_5(dataSet[100:400], ap_list, ap_dict)
    print dt.createTree()
    count = 0
    for i in range(100):
        if dataSet[i][-1] == dt.getLabel(dataSet[i][:-1]):
            count += 1
    for i in range(400, len(dataSet)):
        if dataSet[i][-1] == dt.getLabel(dataSet[i][:-1]):
            count += 1
    print 'correct rate:'
    print float(count) / (len(dataSet) - 300)


