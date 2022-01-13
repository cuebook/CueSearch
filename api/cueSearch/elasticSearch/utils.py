import requests
# from search import app
# from config import METRIC_URL, DIMENSION_URL, DIMENSION_VALUES_URL
from utils.apiResponse import ApiResponse

# from search.globalDimensions.models import GlobalDimension
from cueSearch.models import  GlobalDimension
# from search.globalDimensions.serializer import GlobalDimensionSchema
from cueSearch.serializers import GlobalDimensionSerializer
from dataset.models import Dataset
from access.data import Data


class Utils:
    def getGlobalDimensionForIndex():
        """ Service to get global dimension values for indexing, only published global dimensions are being indexed """  
        # res = ApiResponse() 
        globalDimension = GlobalDimension.objects.filter(published=True)
        data = GlobalDimensionSerializer(globalDimension,many=True).data
        # res.update(True, "Fetched global dimension for indexing", data)
        res = {"success":True, "data":data}
        return res

    # def getMetricsFromCueObserve():
    #     """ Service to get all metrics from cueObserve"""
    #     try:
    #         url = METRIC_URL
    #         response = requests.get(url)
    #         payloads = response.json().get("data", [])
    #         payloadDicts = []
    #         for payload in payloads:
    #             dictObjs = {}
    #             dictObjs["dataset"] = payload["name"]
    #             dictObjs["metrics"] = payload["metrics"]
    #             payloadDicts.append(dictObjs)
    #         res = {"success":True, "data":payloadDicts}
    #         return res
    #     except Exception as ex:
    #         app.logger.error("Failed to get metrics from cueObserve %s", ex)
    #         res = {"success":False, "data":[], "message":"Error occured to get metric from cueObserve"}

    def getDimensionalValuesForDimension(datasetId, dimension):
        try:
            # res = ApiResponse()
            # url = DIMENSION_VALUES_URL
            # data = {"datasetId":datasetId, "dimension":dimension}
            # response = requests.post(url, data=data)
            dataset = Dataset.objects.get(id=datasetId)
            df = Data.fetchDatasetDataframe(dataset)
            data = df[dimension].to_list()[:30]
            # response = GlobalDimensionServices.getDimValues(data)
            # payloads  = response.json().get("data", [])
            res = {"success":True, "data":data}
            # res.update(True, "successfully fetched dimensional values", data)
        except Exception as ex:
            # app.logger.error*("Failed to get dimension %s", ex)
            res = {"success":False, "data":[], "message":"Error occured while getting dimensional values from cueObserve"}
        return res
        
