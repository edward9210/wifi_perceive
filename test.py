from Adapter import Adapter
from DesicionTree import DecisionTree
from DecisionTreeC4_5 import DecisionTreeC4_5


if __name__ == '__main__':
    obj = Adapter('/Users/edward/Desktop/wifi_perceive/data.csv')
    obj.disorganizeData()
    dataSet = obj.data
    print dataSet
    ap_list = obj.ap_list
    ap_dict = obj.ap_dict
    print ap_dict
    dt = DecisionTreeC4_5(dataSet[250:], ap_list, ap_dict)
    print dt.createTree()
    count = 0
    for i in range(0, 250):
        if dataSet[i][-1] == dt.getLabel(dataSet[i][:-1]):
            count += 1
    print count
    print 'correct rate:'
    print float(count) / 250


