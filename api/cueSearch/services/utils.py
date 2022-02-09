from typing import List, Dict
from itertools import groupby
from pandas import DataFrame


def key_func(k):
    return k["dimension"]


def structureAndFilter(params: list):
    """This method is responsible for adding AND filter between dimensionValue belongs to different dimension"""
    text = ""
    for i in range(len(params)):
        if i == 0:
            text = "( " + params[i] + " )"
        else:
            text = "( " + text + " )" + " AND " + "( " + params[i] + " )"
    return text


def structureOrFilter(payload):
    """This method is responsible for adding OR filter between dimensionValue belongs to same dimension"""
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
                text = key + " = " + "'" + value["value"] + "'"
            elif prevKey and prevKey == key:
                text = text + " OR " + key + " = " + "'" + value["value"] + "'"
                prevKey = key
            elif prevKey and prevKey != key:
                l.append(text)
                text = ""
                text = text + key + " = " + "'" + value["value"] + "'"
                prevKey = key
    if text:
        l.append(text)
    return l


def makeFilter(payload):
    """This method is responsible for making datset specific filter"""
    paramList = structureOrFilter(payload)
    filter = structureAndFilter(paramList)
    return filter


def addDimensionsInParam(payload):
    """This method is responsible for grouping all dimension that has used in dataset filter"""
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
    

def getChartMetaData(params: Dict, data: List) -> Dict:
    """
    Calculate meta data for chart rendering UI
    :param params:
    :param data: chart data
    """
    timestampColumn = None
    metric = None
    dimension = None
    mask = "M/D/H"
    order = "0"
    chartMetaData = {}
    if params["renderType"] == "line" and data:
        dataColumns = data[0].keys()
        if params["timestampColumn"] in dataColumns:
            timestampColumn = params["timestampColumn"]
        if params["granularity"] == "day":
            mask = "M/D"
        metric = list(set(params["metrics"]) & set(dataColumns))[0]
        chartMetaData = {
            "xColumn": timestampColumn,
            "yColumn": metric,
            "scale": {
                timestampColumn: {"type": "time", "mask": mask},
            },
            "order": "O",
        }

        try:
            dimension = list(set(params["dimensions"]) & set(dataColumns))[0]
            chartMetaData["color"] = dimension
            chartMetaData["scale"][dimension] = {"alias": dimension}
        except Exception as ex:
            pass

    return chartMetaData
