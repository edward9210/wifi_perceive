from Adapter import Adapter
from DesicionTree import DecisionTree

if __name__ == '__main__':
    obj = Adapter('/Users/edward/Desktop/wifisen/data.csv')
    dataSet = obj.data
    labels = obj.ap_list
    labelsDict = obj.ap_dict
    dt = DecisionTree(dataSet[50:450], labels, labelsDict)
    count = 0
    for i in range(50):
        if dataSet[i][2] == dt.getLabel(dataSet[i][:-1]):
            count += 1
    for i in range(450, len(dataSet)):
        if dataSet[i][2] == dt.getLabel(dataSet[i][:-1]):
            count += 1
    print float(count) / (len(dataSet) - 400)

