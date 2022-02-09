import json
import logging
from utils.apiResponse import ApiResponse
from access.data import Data
from dataset.models import Dataset
from dataset.serializers import DatasetsSerializer, DatasetSerializer
from cueSearch.elasticSearch import ESIndexingUtils
from cueSearch.elasticSearch.utils import Utils


class Datasets:
    """
    Provides services related to dataset
    """

    @staticmethod
    def getDatasets():
        """
        Gets all datasets
        """
        res = ApiResponse("Error in getting datasets")
        datasets = Dataset.objects.all()
        data = DatasetsSerializer(datasets, many=True).data
        res.update(True, "Successfully retrieved datasets", data)
        return res

    @staticmethod
    def getDataset(datasetId: int):
        """
        Gets a dataset
        :param datasetId: id of a dataset
        """
        res = ApiResponse("Error in getting dataset")
        dataset = Dataset.objects.get(id=datasetId)
        data = DatasetSerializer(dataset).data
        res.update(True, "Successfully retrieved dataset", data)
        return res

    @staticmethod
    def updateDataset(datasetId: int, data: dict):
        """
        Updates a dataset
        :param datasetId: id of dataset
        :param data: contains new name and sql for dataset
        """
        res = ApiResponse("Error in updating dataset")
        name = data["name"]
        sql = data["sql"]
        connectionId = data["connectionId"]
        metrics = data["metrics"]
        dimensions = data["dimensions"]
        timestamp = data["timestamp"]
        granularity = data["granularity"]
        isNonRollup = data["isNonRollup"]

        dataset = Dataset.objects.get(id=datasetId)
        dataset.name = name
        dataset.sql = sql
        dataset.connection_id = connectionId
        dataset.metrics = json.dumps(metrics)
        dataset.dimensions = json.dumps(dimensions)
        dataset.timestampColumn = timestamp
        dataset.granularity = granularity
        dataset.isNonRollup = isNonRollup
        dataset.save()
        try:
            ESIndexingUtils.runAllIndexDimension()
        except Exception as ex:
            logging.error("Exception occured while indexing dataset dimension")

        res.update(True, "Successfully updated dataset")
        return res

    @staticmethod
    def deleteDataset(datasetId: int):
        """
        Deletes a dataset
        :param datasetId: id of dataset
        """
        res = ApiResponse("Error in deleting dataset")
        dataset = Dataset.objects.get(id=datasetId)
        dataset.delete()
        try:
            ESIndexingUtils.runAllIndexDimension()
        except Exception as ex:
            logging.error("Exception occured while indexing dataset dimension")

        res.update(True, "Successfully deleted dataset")
        return res

    @staticmethod
    def createDataset(data: dict):
        """
        Creates a dataset
        :param data: contains dataset name and sql
        """
        res = ApiResponse("Error in creating dataset")
        name = data["name"]
        sql = data["sql"]
        connectionId = data["connectionId"]
        metrics = data["metrics"]
        dimensions = data["dimensions"]
        timestamp = data["timestamp"]
        granularity = data["granularity"]
        isNonRollup = data["isNonRollup"]
        Dataset.objects.create(
            name=name,
            sql=sql,
            connection_id=connectionId,
            metrics=json.dumps(metrics),
            dimensions=json.dumps(dimensions),
            timestampColumn=timestamp,
            granularity=granularity,
            isNonRollup=isNonRollup,
        )
        try:
            ESIndexingUtils.runAllIndexDimension()
        except Exception as ex:
            logging.error("Exception occured while indexing dataset dimension")

        res.update(True, "Successfully created dataset")
        return res

    def getDatasetData(params: dict):
        """
        Utility service to fetch data for a payload
        :param payload: Dict containing dataset name, and dataset dimension
        """
        res = ApiResponse("Error in fetching data")
        dataset = Dataset.objects.get(id=params["datasetId"])
        dataDf = Data.fetchDatasetDataframe(dataset, params["sql"])
        data = dataDf.to_dict("records")

        chartMetaData = Utils.addChartMetaData(params, data)
        finaldata = {"data": data, "chartMetaData": chartMetaData}
        res.update(True, "Successfully fetched data", finaldata)
        return res
