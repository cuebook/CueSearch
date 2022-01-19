import asyncio
import logging
import concurrent.futures
from asgiref.sync import async_to_sync, sync_to_async
from django.http import response
import aiohttp
from utils.apiResponse import ApiResponse
from django.template import Template, Context
from cueSearch.serializers import SearchCardTemplateSerializer
from cueSearch.models import SearchCardTemplate
from cueSearch.elasticSearch import ESQueryingUtils, ESIndexingUtils
from dataset.services import Datasets


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
        globalDimensionId = searchPayload[0]["id"]
        globalDimensionValue = searchPayload[0]["label"]

        searchResults = ESQueryingUtils.findGlobalDimensionResults(
            globalDimension = globalDimensionId,
            query = globalDimensionValue
        )
        searchTemplate = SearchCardTemplate.objects.get(id=1) # Temporary for testing, will loop over templates, set here id accordingly
        for result in searchResults:
            result.update({"sqlTemplate": searchTemplate.sql})        

        dataResults = asyncio.run(SearchCardTemplateServices.fetchCardsData(searchResults))
        finalResults = []
        for i in range(len(searchResults)):
            finalResults.append(
                {
                    "title": Template(searchTemplate.title).render(Context(searchResults[i])),
                    "text" : Template(searchTemplate.bodyText).render(Context(searchResults[i])),
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

