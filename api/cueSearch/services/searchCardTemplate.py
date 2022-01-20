import asyncio
import logging
import json
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
    def getCardTemplates():
        """
        Service to fetch all card templates
        """
        res = ApiResponse("Error in fetching card templates")
        try:
            templates = SearchCardTemplate.objects.all()
            data = SearchCardTemplateSerializer(templates,many=True).data
            res.update(True, "Fetched card templates", data)

        except Exception as ex:
            res.update(False,[])
        return res

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
        

    async def fetchCardsData(searchResults):
        """
        Async method to fetch data for searched cards
        :param dataUrl: Url endpoint to fetch data
        :param searchResults: List of dicts containing search results
        """
        async with aiohttp.ClientSession() as session:
            result = await asyncio.gather(*(SearchCardTemplateServices._sendDataRequest(session, obj) for obj in searchResults))
            return result
    
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
                globalDimension = globalDimensionId,
                query = globalDimensionValue
        )
            if results:
                searchResults.extend(results)
        
        groupedResults = groupSearchResultsByDataset(searchResults)
        searchTemplate = SearchCardTemplate.objects.get(id=2) 

        params = []
        for result in groupedResults:
            for key, value in result.items():
                dataset = Dataset.objects.get(id=int(key))
                paramDict = {}
                paramDict["datasetId"] = int(key)
                paramDict["searchResults"] = value
                paramDict["sqlTemplate"] = searchTemplate.sql 
                paramDict["dataset"] = dataset.name
                paramDict["dimensions"] = json.loads(dataset.dimensions)
                paramDict["metrics"] = json.loads(dataset.metrics)
                paramDict["timestamp"] = dataset.timestampColumn
                params.append(paramDict)

        for param in params:
            filter = makeFilter(param)
            dimensions = addDimensionsInParam(param)
            param.update({"filter" : filter})
            param.update({"filterDimensions": dimensions})
        
        dataResults = asyncio.run(SearchCardTemplateServices.fetchCardsData(params))
        for i in range(len(params)):
            finalResults.append(
                {
                    "title": Template(searchTemplate.title).render(Context(params[i])),
                    "text" : Template(searchTemplate.bodyText).render(Context(params[i])),
                    "data": dataResults[i]
                })
        res.update(True, "successfully fetched",finalResults)
        return res


        
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
    return k['datasetId']

def groupSearchResultsByDataset(searchResults):
    results = []
    searchResults = sorted(searchResults, key=key_func)
    for key, value in groupby(searchResults, key_func):
        value = list(value)
        results.append({key:value})
    return results
        
    