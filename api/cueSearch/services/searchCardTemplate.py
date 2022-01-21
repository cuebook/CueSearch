import asyncio
import logging
import json
from typing import List, Dict
from itertools import groupby
import concurrent.futures
from asgiref.sync import async_to_sync, sync_to_async
from django.http import response
import aiohttp
from utils.apiResponse import ApiResponse
from django.template import Template, Context
from cueSearch.serializers import SearchCardTemplateSerializer
from cueSearch.models import SearchCardTemplate
from dataset.models import Dataset
from cueSearch.elasticSearch import ESQueryingUtils, ESIndexingUtils
from dataset.services import Datasets
from cueSearch.services.utils import addDimensionsInParam, makeFilter

class SearchCardTemplateServices:
    """
    Service for various Card template operations
    """

    @staticmethod
    def getCardTemplates():
        """
        Service to fetch all card templates
        """
        res = ApiResponse("Error in fetching card templates")
        try:
            templates = SearchCardTemplate.objects.all()
            data = SearchCardTemplateSerializer(templates, many=True).data
            res.update(True, "Fetched card templates", data)

        except Exception as ex:
            res.update(False, [])
        return res

    @staticmethod
    async def _sendDataRequest(session, payload):
        """
        Async method to fetch individual search card data
        :param session: ClientSession instance for aiohttp
        :param dataUrl: Url endpoint to fetch data
        :param payload: Dict containing parameters for fetching data
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, Datasets.getDatasetData, payload)
        responseData = result.json()
        return responseData

    @staticmethod
    async def fetchCardsData(searchResults):
        """
        Async method to fetch data for searched cards
        :param dataUrl: Url endpoint to fetch data
        :param searchResults: List of dicts containing search results
        """
        async with aiohttp.ClientSession() as session:
            result = await asyncio.gather(
                *(
                    SearchCardTemplateServices._sendDataRequest(session, obj)
                    for obj in searchResults
                )
            )
            return result

    @staticmethod
    def getSearchCards(searchPayload: dict):
        """
        Service to fetch and create search cards on the fly
        :param searchPayload: Dict containing the search payload
        """
        res = ApiResponse()
        finalResults = []
        searchResults = []
        for payload in searchPayload:
            results = []
            globalDimensionId = payload["id"]
            globalDimensionValue = payload["label"]

            results = ESQueryingUtils.findGlobalDimensionResults(
                globalDimension=globalDimensionId, query=globalDimensionValue
            )
            if results:
                searchResults.extend(results)

        groupedResults = groupSearchResultsByDataset(searchResults)
        searchTemplates = SearchCardTemplate.objects.all()

        params = []
        for searchTemplate in searchTemplates:
            for result in groupedResults:
                for key, value in result.items():
                    dataset = Dataset.objects.get(id=int(key))
                    paramDict = {}
                    paramDict["datasetId"] = int(key)
                    paramDict["searchResults"] = value
                    paramDict["sqlTemplate"] = searchTemplate.sql
                    paramDict["templateTitle"] = searchTemplate.title
                    paramDict["templateText"] = searchTemplate.bodyText
                    paramDict["renderType"] = searchTemplate.renderType
                    paramDict["dataset"] = dataset.name
                    paramDict["dimensions"] = json.loads(dataset.dimensions)
                    paramDict["metrics"] = json.loads(dataset.metrics)
                    paramDict["timestampColumn"] = dataset.timestampColumn
                    paramDict["datasetSql"] = dataset.sql
                    paramDict["granularity"] = dataset.granularity
                    params.append(paramDict)

        for param in params:
            filter = makeFilter(param)
            dimensions = addDimensionsInParam(param)
            param.update({"filter": filter})
            param.update({"filterDimensions": dimensions})

        dataResults = asyncio.run(SearchCardTemplateServices.fetchCardsData(params))
        for i in range(len(params)):
            finalResults.append(
                {
                    "title": Template(params[i]["templateTitle"]).render(
                        Context(params[i])
                    ),
                    "text": Template(params[i]["templateText"]).render(
                        Context(params[i])
                    ),
                    "data": dataResults[i],
                    "params": params[i],
                }
            )

        finalResults = [ SearchCardTemplateServices.addChartMetaData(x) for x in finalResults ]
        res.update(True, "successfully fetched", finalResults)
        return res

    @staticmethod
    def addChartMetaData(result: Dict) -> Dict:
        """
        Adds metadata needed for chart to result
        """
        timestampColumn = None
        metric = None
        dimension = None
        mask = "M/D/H"
        order = "0"
        chartMetaData = {}

        params = result['params']
        if params['renderType'] == "line" and result['data'] and result['data']['data']:
            dataColumns = result['data']['data'][0].keys()
            if params['timestampColumn'] in dataColumns:
                timestampColumn = params["timestampColumn"]
            if params['granularity'] == "day":
                mask = "M/D"
            metric = list(set(params["metrics"]) & set(dataColumns))[0]

            chartMetaData = {
                "xColumn": timestampColumn,
                "yColumn": metric,
                "scale": {
                    timestampColumn: {
                        'type': 'time',
                        'mask': mask
                    },
                },
                "order": "O"
            }

            try:
                dimension = list(set(params["dimensions"]) & set(dataColumns))[0]
                chartMetaData['color'] = dimension
                chartMetaData["scale"][dimension] = { 'alias': dimension}
            except Exception as ex:
                pass

        result['chartMetaData'] = chartMetaData
        return result


    @staticmethod
    def getSearchSuggestions(query):
        """Get searchsuggestion for search dropdown"""
        res = ApiResponse()
        data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    ESQueryingUtils.findGlobalDimensionResultsForSearchSuggestion,
                    query=query,
                    datasource=None,
                    offset=0,
                    limit=6,
                ),
                executor.submit(
                    ESQueryingUtils.findGlobalDimensionNames,
                    query=query,
                    datasource=None,
                    offset=0,
                    limit=4,
                ),
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    data.extend(future.result())
                except Exception as ex:
                    logging.error("Error in fetching search suggestions :%s", str(ex))
        res.update(True, "success", data)
        return res


def key_func(k):
    return k["datasetId"]


def groupSearchResultsByDataset(searchResults):
    results = []
    searchResults = sorted(searchResults, key=key_func)
    for key, value in groupby(searchResults, key_func):
        value = list(value)
        results.append({key: value})
    return results
