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
from cueSearch.services.utils import (
    addDimensionsInParam,
    makeFilter,
    getOrderFromDataframe,
)

logger = logging.getLogger(__name__)


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

    # @staticmethod
    # async def _sendDataRequest(session, payload):
    #     """
    #     Async method to fetch individual search card data
    #     :param session: ClientSession instance for aiohttp
    #     :param dataUrl: Url endpoint to fetch data
    #     :param payload: Dict containing parameters for fetching data
    #     """
    #     loop = asyncio.get_event_loop()
    #     result = await loop.run_in_executor(None, Datasets.getDatasetData, payload)
    #     responseData = result.json()
    #     return responseData

    # @staticmethod
    # async def fetchCardsData(searchResults):
    #     """
    #     Async method to fetch data for searched cards
    #     :param dataUrl: Url endpoint to fetch data
    #     :param searchResults: List of dicts containing search results
    #     """
    #     async with aiohttp.ClientSession() as session:
    #         result = await asyncio.gather(
    #             *(
    #                 SearchCardTemplateServices._sendDataRequest(session, obj)
    #                 for obj in searchResults
    #             )
    #         )
    #         return result

    @staticmethod
    def getSearchCardData():  # searchPayload
        """
        Async method to fetch individual search card data
        :param payload: Dict containing parameters for fetching data
        """
        searchPayload = [
            {
                "params": {
                    "datasetId": 1,
                    "searchResults": [
                        {
                            "value": "AP",
                            "dimension": "DeliveryRegion",
                            "globalDimensionName": "Data",
                            "user_entity_identifier": "Data",
                            "id": 8,
                            "dataset": "Test data",
                            "datasetId": 1,
                            "type": "GLOBALDIMENSION",
                        }
                    ],
                    "filter": "( DeliveryRegion = 'AP' )",
                    "filterDimensions": ["DeliveryRegion"],
                    "templateSql": " {% for metric in metrics %} SELECT ({{ timestampColumn }}), SUM({{ metric }}) as {{ metric }} FROM ({{ datasetSql|safe }}) WHERE {{filter|safe}} GROUP BY 1 limit 500 +-; {% endfor %}",
                    "templateTitle": ' {% for metric in metrics %}  <span style="background:#eeeeee; padding: 0 4px; border-radius: 4px;">Dataset = {{dataset}} , Filter = {{filter}}</span> +-; {% endfor %}',
                    "templateText": ' {% for metric in metrics %} For <span style="background:#eeeeee; padding: 0 4px; border-radius: 4px;">{{filter}}</span>  +-; {% endfor %}',
                    "renderType": "line",
                    "dataset": "Test data",
                    "dimensions": ["DeliveryRegion", "Brand", "WarehouseCode"],
                    "metrics": ["ReturnEntries", "RefundAmount"],
                    "timestampColumn": "ReturnDate",
                    "datasetSql": "SELECT DATE_TRUNC('DAY', __time) as ReturnDate,\nDeliveryRegionCode as DeliveryRegion, P_BRANDCODE as Brand, WarehouseCode,\nSUM(\"count\") as ReturnEntries, sum(P_FINALREFUNDAMOUNT) as RefundAmount\nFROM RETURNENTRY\nWHERE __time >= CURRENT_TIMESTAMP - INTERVAL '13' MONTH \nGROUP BY 1, 2, 3, 4\nORDER BY 1",
                    "granularity": "day",
                },
                "title": '   <span style="background:#eeeeee; padding: 0 4px; border-radius: 4px;">Dataset = Test data , Filter = ( DeliveryRegion = &#x27;AP&#x27; )</span> ',
                "text": '  For <span style="background:#eeeeee; padding: 0 4px; border-radius: 4px;">( DeliveryRegion = &#x27;AP&#x27; )</span>  ',
                "sql": "  SELECT (ReturnDate), SUM(RefundAmount) as RefundAmount FROM (SELECT DATE_TRUNC('DAY', __time) as ReturnDate,\nDeliveryRegionCode as DeliveryRegion, P_BRANDCODE as Brand, WarehouseCode,\nSUM(\"count\") as ReturnEntries, sum(P_FINALREFUNDAMOUNT) as RefundAmount\nFROM RETURNENTRY\nWHERE __time >= CURRENT_TIMESTAMP - INTERVAL '13' MONTH \nGROUP BY 1, 2, 3, 4\nORDER BY 1) WHERE ( DeliveryRegion = 'AP' ) GROUP BY 1 limit 500 ",
            }
        ]
        res = ApiResponse("Data not fetched")
        # searchResults = {key: searchPayload[key] for key in searchPayload.keys()
        # & {'data'}}
        for searchItems in searchPayload:
            result = Datasets.getDatasetData(searchItems)
            response = result.json()
            print("-------------Response------------------", response)
            res.update(True, "Data fetch Successfully", response)
        return res

    @staticmethod
    def ElasticSearchQueryResultsForOnSearchQuery(searchPayload: dict):
        searchResults = []
        for payload in searchPayload:
            data = []
            query = payload["label"]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                if payload["searchType"] == "GLOBALDIMENSION":
                    futures = [
                        executor.submit(
                            ESQueryingUtils.findGlobalDimensionResults, query=query
                        ),
                    ]
                elif payload["searchType"] == "DATASETDIMENSION":
                    futures = [
                        executor.submit(
                            ESQueryingUtils.findNonGlobalDimensionResults,
                            globalDimension=payload["globalDimensionId"],
                            query=query,
                        ),
                    ]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        data.extend(future.result())
                    except Exception as ex:
                        logging.error(
                            "Error in fetching search suggestions :%s", str(ex)
                        )

            if data:
                searchResults.extend(data)
        # searchResults = list({v['id']:v for v in searchResults}.values())
        return searchResults

    @staticmethod
    def getSearchCards(searchPayload: dict):
        """
        Service to fetch and create search cards on the fly
        :param searchPayload: Dict containing the search payload
        """
        res = ApiResponse()
        finalResults = []
        searchResults = []
        searchResults = (
            SearchCardTemplateServices.ElasticSearchQueryResultsForOnSearchQuery(
                searchPayload
            )
        )
        groupedResults = groupSearchResultsByDataset(searchResults)
        searchTemplates = SearchCardTemplate.objects.all()

        results = []
        for searchTemplate in searchTemplates:
            for result in groupedResults:
                for datasetId, datasetSearchResult in result.items():
                    dataset = Dataset.objects.get(id=int(datasetId))
                    paramDict = {}
                    paramDict["datasetId"] = int(datasetId)

                    paramDict["searchResults"] = datasetSearchResult
                    paramDict["filter"] = makeFilter(datasetSearchResult)
                    paramDict["filterDimensions"] = addDimensionsInParam(
                        datasetSearchResult
                    )

                    paramDict["templateSql"] = searchTemplate.sql
                    paramDict["templateTitle"] = searchTemplate.title
                    paramDict["templateText"] = searchTemplate.bodyText
                    paramDict["renderType"] = searchTemplate.renderType

                    paramDict["dataset"] = dataset.name
                    paramDict["dimensions"] = json.loads(dataset.dimensions)
                    paramDict["metrics"] = json.loads(dataset.metrics)
                    paramDict["timestampColumn"] = dataset.timestampColumn
                    paramDict["datasetSql"] = dataset.sql
                    paramDict["granularity"] = dataset.granularity

                    renderedTemplates = SearchCardTemplateServices.renderTemplates(
                        paramDict
                    )
                    for renderedTemplate in renderedTemplates:
                        x = {"params": paramDict, **renderedTemplate}
                        results.append(x)
        # dataResults = asyncio.run(SearchCardTemplateServices.getSearchCardData(results))
        datasetResult = []
        for i in range(len(results)):
            results[i]["data"] = datasetResult

        finalResults = [SearchCardTemplateServices.addChartMetaData(x) for x in results]
        res.update(True, "successfully fetched", finalResults)
        return res

    @staticmethod
    def renderTemplates(param: dict):
        """
        Renders template with passed variables
        :param param: dict with values needed for rendering
        returns: [{ title: str, text: str, sql: str }]
        """
        response = []
        delimiter = "+-;"
        try:
            titles = (
                Template(param["templateTitle"]).render(Context(param)).split(delimiter)
            )
            texts = (
                Template(param["templateText"]).render(Context(param)).split(delimiter)
            )
            sqls = (
                Template(param["templateSql"]).render(Context(param)).split(delimiter)
            )

            if len(titles) != len(texts) or len(titles) != len(sqls):
                raise ValueError(
                    "Incosistent use of delimiter (%s) in title, text, sql of template"
                    % delimiter
                )

            for i in range(len(sqls)):
                if str.isspace(sqls[i]):
                    continue
                response.append({"title": titles[i], "text": texts[i], "sql": sqls[i]})

        except Exception as ex:
            logger.error("Error in rendering templates: %s", str(ex))
            logger.error(param)

        return response

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

        params = result["params"]
        if params["renderType"] == "line" and result["data"] and result["data"]["data"]:
            dataColumns = result["data"]["data"][0].keys()
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

        result["chartMetaData"] = chartMetaData
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
                    limit=8,
                ),
                executor.submit(
                    ESQueryingUtils.findNonGlobalDimensionResultsForSearchSuggestion,
                    query=query,
                    datasource=None,
                    offset=0,
                    limit=8,
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
