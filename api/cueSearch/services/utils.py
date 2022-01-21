from itertools import groupby
from pandas import DataFrame

def key_func(k):
    return k['dimension']

def structureAndFilter(params: list):

    text = ""
    for i in range(len(params)):
        if i == 0:
            text ="( " + params[i] + " )" 
        else: 
            text = "( " + text + " )" +" AND "+ "( "+ params[i] + " )"
    return text
                
def structureOrFilter(payload):
    payload = sorted(payload, key=key_func)

    prevKey = None
    text = ""
    l = []
    for key, values in groupby(payload, key_func):
        for value in values:
            # print(key)
            # print(value)
            if not prevKey:
                prevKey = key
                text = key + " = "+"'"+ value['value']+"'"
            elif prevKey and prevKey == key:
                text = text + " OR "  + key + " = "+ "'"+ value['value']+"'"
                prevKey = key
            elif prevKey and prevKey != key:
                l.append(text)
                text = ""
                text = text + key + " = " + "'"+ value['value']+"'"
                prevKey = key
    if text:
        l.append(text)
    return l 

def makeFilter(payload):
    paramList = structureOrFilter(payload)
    filter = structureAndFilter(paramList)
    return filter

def addDimensionsInParam(payload):
    payload = sorted(payload, key=key_func)
    listOfDimensions = []
    for key, values in groupby(payload, key_func):
        listOfDimensions.append(key)
    return listOfDimensions


def getOrderFromDataframe(dataframe: DataFrame, column: str):
    try:
        minValue = dataframe[column].min(skipna=True)
    except:
        minValue = 0
    if isinstance(minValue, (int, float)):
        order = (
            "B"
            if minValue > 1000000000
            else ("M" if minValue > 1000000 else ("K" if minValue > 1000 else "O"))
        )
    else:
        order = "O"
    return order
