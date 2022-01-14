import asyncio

from django.template.base import constant_string
import aiohttp
from utils.apiResponse import ApiResponse

# from flask import render_template_string
# from search import app, db
# from django.template.loader import render_to_string
from django.template import Template, Context

import logging
# from .models import SearchCardTemplate
from cueSearch.serializers import SearchCardTemplateSerializer
# from elasticSearch.elastic_search_querying import ESQueryingUtils
# from config import DATASET_URL
from cueSearch.models import SearchCardTemplate
import concurrent.futures
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
            # app.logger.info("Getting card templates")
            templates = SearchCardTemplate.objects.all()
            data = SearchCardTemplateSerializer(templates,many=True).data
            res.update(True, "Fetched card templates", data)

        except Exception as ex:
            # app.logger.error(f"Failed to get card templates {ex}")
            res.update(False,[])
        return res

    async def _sendDataRequest(session, payload):
        """
        Async method to fetch individual search card data
        :param session: ClientSession instance for aiohttp
        :param dataUrl: Url endpoint to fetch data
        :param payload: Dict containing parameters for fetching data
        """
        dataUrl = "http://localhost:8000/api/dataset/data/"  # will remove it and call function directly for it 
        resp = await session.post(dataUrl, json=payload)
        responseData = await resp.json()
        # resp = await Datasets.getDatasetData(payload)
        # print('resp', resp)
        # responseData = await resp.data  # or resp.data
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
        # Temporary for testing # for globalDimensionValues only 
        res = ApiResponse()
        # gdValuesObjs = searchPayload.get("globalDimensionValuesPayload", [[]])
        # globalDimensionId = gdValuesObjs[0].get("globalDimensionId", None)
        # gdValues = gdValuesObjs[0].get("globalDimensionValue", [])
        globalDimensionId = searchPayload[0]["id"]
        globalDimensionValue = searchPayload[0]["label"]

        searchResults = ESQueryingUtils.findGlobalDimensionResults(
            globalDimension = globalDimensionId,
            query = globalDimensionValue
        )
        # print("searchResults", searchResults)
        searchTemplate = SearchCardTemplate.objects.get(id=1) # Temporary for testing, will loop over templates, set here id accordingly
        print("searachTemplate", searchTemplate.sql)
        for result in searchResults:
            result.update({"sqlTemplate": searchTemplate.sql})        

        dataResults = asyncio.run(SearchCardTemplateServices.fetchCardsData(searchResults))
        print("dataResults", dataResults)
        finalResults = []
        print("searchResults", searchResults)
        for i in range(len(searchResults)):
            finalResults.append(
                {
                    "title": Template(searchTemplate.title).render(Context(searchResults[i])),
                    "text" : Template(searchTemplate.bodyText).render(Context(searchResults[i])),
                    "data": dataResults[i]
                })
        print('finalResult', finalResults)
        res.update(True, "successfully fetched",finalResults)
        return res


        
    def getSearchSuggestions(query):
        # app.logger.debug("Calling the query ES API and fetching only the top 10 results")
        # res = ApiResponse("Error in fetching search suggestion ")
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
                    # app.logger.info("data %s",data)
                except Exception as ex:
                    # app.logger.error("Error in fetching search suggestions :%s", str(ex))
                    logging.error("Error in fetching search suggestions :%s", str(ex))
        # res.update(True, "fetched search suggestion", data)
        res.update(True, "success", data)
        # res = {"success":True, "data":data}
        return res

