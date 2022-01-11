import requests
from search import app
from config import METRIC_URL, DIMENSION_URL, DIMENSION_VALUES_URL
from search.globalDimensions.models import GlobalDimension
from search.globalDimensions.serializer import GlobalDimensionSchema

class Utils:
    def getGlobalDimensionForIndex():
        """ Service to get global dimension values for indexing, only published global dimensions are being indexed """   
        globalDimension = GlobalDimension.query.filter_by(published=True)
        data = GlobalDimensionSchema(many=True).dump(globalDimension)   
        res = {"success":True, "data":data}
        return res

    def getMetricsFromCueObserve():
        """ Service to get all metrics from cueObserve"""
        try:
            url = METRIC_URL
            response = requests.get(url)
            payloads = response.json().get("data", [])
            payloadDicts = []
            for payload in payloads:
                dictObjs = {}
                dictObjs["dataset"] = payload["name"]
                dictObjs["metrics"] = payload["metrics"]
                payloadDicts.append(dictObjs)
            res = {"success":True, "data":payloadDicts}
            return res
        except Exception as ex:
            app.logger.error("Failed to get metrics from cueObserve %s", ex)
            res = {"success":False, "data":[], "message":"Error occured to get metric from cueObserve"}

    def getDimensionalValuesForDimension(datasetId, dimension):
        try:
            url = DIMENSION_VALUES_URL
            data = {"datasetId":datasetId, "dimension":dimension}
            response = requests.post(url, data=data)
            payloads  = response.json().get("data", [])
            res = {"success":True, "data":payloads}
            return res
        except Exception as ex:
            app.logger.error*("Failed to get dimension %s", ex)
            res = {"success":False, "data":[], "message":"Error occured while getting dimensional values from cueObserve"}
