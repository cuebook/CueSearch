import logging
from utils.apiResponse import ApiResponse
from dataset.models import Dataset
from cueSearch.models import GlobalDimensionValues, GlobalDimension
from cueSearch.serializers import AllDimensionsSerializer, GlobalDimensionSerializer
from access.data import Data

from cueSearch.elasticSearch import ESIndexingUtils


class GlobalDimensionServices:
    """Services for Global Dimension"""

    def createGlobalDimension(payloads):
        """Create global dimension"""
        try:
            res = ApiResponse("Error in creating dimensionalValues")
            name = payloads["name"]
            globalDimension = GlobalDimension.objects.create(name=name)
            objs = payloads["dimensionalValues"]
            dimensionalValueObjs = []
            for obj in objs:
                datasetId = int(obj["datasetId"])
                dataset = Dataset.objects.get(id=datasetId)
                GlobalDimensionValues.objects.create(
                    dataset=dataset,
                    dimension=obj["dimension"],
                    globalDimension=globalDimension,
                )
            try:
                ESIndexingUtils.runAllIndexDimension()
            except Exception as ex:
                logging.error("Exception occured while indexing global dimension")

            res.update(True, "GlobalDimension created successfully")
        except Exception as ex:
            res.update(False, "Global Dimension name already exists")
        return res

    def deleteGlobalDimension(globalDimensionId):
        """Delete globaldimension of given id"""
        try:
            res = ApiResponse("Error occurs while deleting global dimension")
            globalDimension = GlobalDimension.objects.filter(
                id=globalDimensionId
            ).delete()
            try:
                ESIndexingUtils.runAllIndexDimension()
            except Exception as ex:
                logging.error("Exception occured while indexing global dimension")

            res.update(True, "successfully deleted")
        except Exception as ex:
            res.update(False, "Error occured while deleting global dimension ")
        return res

    def getDimension():
        """Get dimension from cueSearch"""
        try:
            res = ApiResponse()
            datasets = Dataset.objects.all().order_by("-id")  # Get all datasets
            data = AllDimensionsSerializer(datasets, many=True).data
            payloads = data
            payloadDicts = []
            for payload in payloads:
                for dimension in payload.get("dimensions", []):
                    dictObjs = {}
                    dictObjs["dataset"] = payload["name"]
                    dictObjs["datasetId"] = payload["id"]
                    dictObjs["dimension"] = dimension
                    payloadDicts.append(dictObjs)

            res.update(True, "Successfully get dimension of datasets ", payloadDicts)
        except Exception as ex:
            res.update(False, "Successfully get dimension of datasets ", [])

        return res

    def getGlobalDimensions():
        """Services to get Global dimension and their linked dimension"""
        res = ApiResponse("Error while fetching global dimensions")
        try:
            globalDimensions = GlobalDimension.objects.all().order_by("-id")
            data = GlobalDimensionSerializer(globalDimensions, many=True).data
            res.update(True, "Successfully fetched global dimension data", data)
        except Exception as ex:
            res.update(False, "Error occured to get data in global dimension", [])
        return res

    def publishGlobalDimension(payload):
        """Service to publish / unpublish global dimension"""
        try:
            res = ApiResponse()
            published = payload.get("published", False)
            globalDimensionId = payload.get("id", None)
            if globalDimensionId:
                globalDimensionObj = GlobalDimension.objects.get(id=globalDimensionId)
                globalDimensionObj.published = published
                globalDimensionObj.save()
                try:
                    ESIndexingUtils.runAllIndexDimension()
                except Exception as ex:
                    logging.error("Exception occured while indexing global dimension")

                res.update(True, "Global Dimension updated successfully")
            else:
                res.update(False, "Id is mandatory")
        except Exception as ex:
            res.update(False, "Error occured while updating global dimension")
        return res

    def getGlobalDimensionById(id):
        """Service to get global dimension of given id"""
        try:
            res = ApiResponse("Error occurs while fetching global dimension by Id")
            globalDimensionObj = GlobalDimension.objects.get(id=id)
            data = GlobalDimensionSerializer(globalDimensionObj).data
            res.update(True, "Successfully fetched global dimension Id", data)

        except Exception as ex:
            res.update(False, "Error occurs while fetching global dimension by Id", [])
        return res

    def updateGlobalDimensionById(id, payload):
        try:
            res = ApiResponse()
            name = payload.get("name", "")
            objs = payload.get("dimensionalValues", [])
            published = payload.get("published", False)
            globalDimension = GlobalDimension.objects.get(id=id)
            newId = globalDimension.id
            globalDimension.delete()
            gd = GlobalDimension.objects.create(
                id=newId, name=name, published=published
            )
            for obj in objs:
                datasetId = int(obj["datasetId"])
                dataset = Dataset.objects.get(id=datasetId)
                gdValues = GlobalDimensionValues.objects.create(
                    dataset=dataset, dimension=obj["dimension"], globalDimension=gd
                )
            try:
                ESIndexingUtils.runAllIndexDimension()
            except Exception as ex:
                logging.error("Indexing Failed")
            res.update(True, "Global Dimension updated successfully")
        except Exception as ex:
            res.update(False, "Error occured while updating global dimension")
        return res

    def nonGlobalDimensionForIndexing():
        """Method to filter dimension from all ready created global dimension"""
        try:
            dimensions = GlobalDimensionServices.getDimension()
            dimensionObjs = dimensions.json().get("data", [])
            globalDim = GlobalDimensionServices.getGlobalDimensions()
            globalDimensionObjs = globalDim.json().get("data", [])
            gdValuesList = []
            listToIndex = []

            for gd in globalDimensionObjs:
                gdValuesList.extend(gd["values"])
            for dimensionObj in dimensionObjs:
                flag = False
                for globalDimensionObj in gdValuesList:
                    if (
                        dimensionObj["datasetId"] == globalDimensionObj["datasetId"]
                    ) and (
                        dimensionObj["dimension"] == globalDimensionObj["dimension"]
                    ):
                        flag = True

                if not flag:
                    listToIndex.append(dimensionObj)
            print(len(listToIndex))
            res = {"success": True, "data": listToIndex}

        except Exception as ex:
            logging.error(
                "Error occued while fetch auto global dimension for indexing %s",
                str(ex),
            )
            res = {"success": False, "data": []}
        return res
