from cueSearch.models import GlobalDimension
from cueSearch.serializers import GlobalDimensionSerializer
from dataset.models import Dataset
from access.data import Data
from typing import List, Dict


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
            data = df[dimension].to_list()[:30]
            res = {"success": True, "data": data}
        except Exception as ex:
            res = {
                "success": False,
                "data": [],
                "message": "Error occured while getting dimensional values from cueObserve",
            }
        return res

    @staticmethod
    def addChartMetaData(params: Dict, data: List) -> Dict:
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
