from cueSearch.models import GlobalDimension
from cueSearch.serializers import GlobalDimensionSerializer
from dataset.models import Dataset
from access.data import Data


class Utils:
    def getGlobalDimensionForIndex():
        """Service to get global dimension values for indexing, only published global dimensions are being indexed"""
        globalDimension = GlobalDimension.objects.filter(published=True)
        data = GlobalDimensionSerializer(globalDimension, many=True).data
        res = {"success": True, "data": data}
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
            dataset = Dataset.objects.get(id=datasetId)
            df = Data.fetchDatasetDataframe(dataset)
            data = df[dimension].to_list()
            data = list(set(data))
            res = {"success": True, "data": data}
        except Exception as ex:
            res = {
                "success": False,
                "data": [],
                "message": "Error occured while getting dimensional values from cueObserve",
            }
        return res
