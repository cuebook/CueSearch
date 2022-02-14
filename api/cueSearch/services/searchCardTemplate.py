import logging
import json
import aiohttp
from typing import Dict
from itertools import groupby
import concurrent.futures
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
    getChartMetaData,
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
                        x = {
                            "params": {**paramDict, "sql": renderedTemplate["sql"]},
                            **renderedTemplate,
                        }
                        results.append(x)

        res.update(True, "successfully fetched", results)
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
                    "Inconsistent use of delimiter (%s) in title, text, sql of template"
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
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    data.extend(future.result())
                except Exception as ex:
                    logging.error("Error in fetching search suggestions :%s", str(ex))
        res.update(True, "success", data)
        return res

    def getSearchCardData(params: dict):
        """
        Utility service to fetch data for a payload
        :param params: Dict containing dataset name, and dataset dimension
        """
        res = ApiResponse("Error in fetching data")
        data = Datasets.getDatasetData(params).data
        print("data ----- ", data[:15])
        chartMetaData = getChartMetaData(params, data)
        finaldata = {"data": data, "chartMetaData": chartMetaData}
        res.update(True, "Successfully fetched data", finaldata)
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
