import os
import time
import logging
from typing import List, Dict
from collections import deque

# from search import app
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from datetime import datetime

# from config import ELASTICSEARCH_URL
import threading
from .utils import Utils

import traceback

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200/")


class ESIndexingUtils:
    """
    Class to handle Elastic Search related indexing
    and search utilities
    """

    GLOBAL_DIMENSIONS_NAMES_INDEX_NAME = (
        "cuesearch_global_dimensions_names_for_search_index"
    )
    GLOBAL_DIMENSIONS_INDEX_NAME = "global_dimensions_name_index_cuesearch"
    GLOBAL_DIMENSIONS_INDEX_DATA = "cuesearch_global_dimensions_data_index"
    AUTO_GLOBAL_DIMENSIONS_INDEX_DATA = "cuesearch_auto_global_dimensions_data_index"
    AUTO_GLOBAL_DIMENSIONS_INDEX_DATA_SEARCH_SUGGESTION = (
        "cuesearch_auto_global_dimensions_search_suggestion_data_index"
    )
    GLOBAL_DIMENSIONS_INDEX_SEARCH_SUGGESTION_DATA = (
        "cuesearch_global_dimensions_search_suggestion_data_index"
    )
    DATASET_MEASURES_INDEX_NAME = "dataset_measures_index_cuesearch"

    @staticmethod
    def _getESClient() -> Elasticsearch:
        """
        Method to get the ES Client
        """
        esHost = ELASTICSEARCH_URL
        esClient = Elasticsearch(hosts=[esHost], timeout=30)
        return esClient

    @staticmethod
    def initializeIndex(indexName: str, indexDefinition: dict) -> str:
        """
        Method to name the index in Elasticsearch
        :indexName: the index name to be used for index creation
        :indexDefinition: the index definition - dict.
        """
        esClient = ESIndexingUtils._getESClient()
        logging.info("intializing Index here ...")
        currentIndexVersion = "_" + str(int(round(time.time() * 1000)))

        aliasIndex = indexName + currentIndexVersion
        logging.info("Creating index of: %s", aliasIndex)
        esClient.indices.create(index=aliasIndex, body=indexDefinition)

        return aliasIndex

    @staticmethod
    def ingestIndex(documentsToIndex: List[Dict], aliasIndex: str):
        """
        Method to ingest data into the index
        :param documentsToIndex The documents that need to be indexed.e.g,
        List of Cards or List of Global Dimensions
        :aliasIndex: the index name to be used for ingestion
        """
        esClient = ESIndexingUtils._getESClient()

        for documentToIndex in documentsToIndex:
            documentToIndex["_index"] = aliasIndex
            documentToIndex["_op_type"] = "index"
        logging.debug("Parallel indexing process starting.")

        deque(parallel_bulk(esClient, documentsToIndex), maxlen=0)

        logging.info("Alias index created at: %s", aliasIndex)

    @staticmethod
    def deleteOldIndex(indexName: str, aliasIndex: str):
        """
        Method to ingest data into the index
        :param documentsToIndex The documents that need to be indexed.e.g,
        List of Cards or List of Global Dimensions
        :aliasIndex: the index name to be used for ingestion
        """
        esClient = ESIndexingUtils._getESClient()

        logging.info(
            "Now point the alias index: { %s } to  { %s }", aliasIndex, indexName
        )
        esClient.indices.put_alias(index=aliasIndex, name=indexName)

        logging.info("Now delete the older indices. They are of no use now.")
        # Now delete the older indices following a certain pattern.
        # Those indices are old indices and are of no use.
        allAliases = esClient.indices.get_alias("*")
        for key, value in allAliases.items():

            logging.debug("Checking for index: %s", key)
            # delete only the indexes matching the given pattern,
            # retain all the other indexes they may be coming from some other source
            if indexName in key:
                # do not delete the current index
                if aliasIndex == key:
                    continue

                logging.info("Deleting the index: %s", key)
                esClient.indices.delete(index=key, ignore=[400, 404])

    @staticmethod
    def deleteAllIndex():
        logging.info("Deleting all indexes")
        esClient = ESIndexingUtils._getESClient()

        allAliases = esClient.indices.get_alias("*")
        for key, value in allAliases.items():

            logging.info("Deleting the index: %s", key)
            esClient.indices.delete(index=key, ignore=[400, 404])
        logging.info("All indexes deleted !")

    @staticmethod
    def _createIndex(
        documentsToIndex: List[Dict], indexName: str, indexDefinition: dict
    ):
        """
        Method to create an index in Elasticsearch
        :param documentsToIndex The documents that need to be indexed.e.g,
        List of Cards or List of Global Dimensions
        :indexName: the index name to be used for index creation
        :indexDefinition: the index definition - dict.
        """

        aliasIndex = ESIndexingUtils.initializeIndex(indexName, indexDefinition)

        # ingest entries in the initialized index

        ESIndexingUtils.ingestIndex(documentsToIndex, aliasIndex)

        # at this stage index has been created at a new location
        # now change the alias of the main Index to point to the new index

        ESIndexingUtils.deleteOldIndex(indexName, aliasIndex)

    @staticmethod
    def runAllIndexDimension():
        """
        Method to spawn a thread to index global dimension into elasticsearch existing indices
        The child thread assumes an index existing with a predefined unaltered indexDefinition
        """
        logging.info("Indexing starts on global dimension action")
        cardIndexer1 = threading.Thread(
            target=ESIndexingUtils.indexGlobalDimensionsDataForSearchSuggestion
        )
        cardIndexer1.start()
        cardIndexer2 = threading.Thread(
            target=ESIndexingUtils.indexGlobalDimensionsData
        )
        cardIndexer2.start()
        cardIndexer3 = threading.Thread(
            target=ESIndexingUtils.indexNonGlobalDimensionsDataForSearchSuggestion
        )
        cardIndexer3.start()
        cardIndexer4 = threading.Thread(
            target=ESIndexingUtils.indexNonGlobalDimensionsData()
        )
        cardIndexer4.start()
        logging.info("Indexing completed !! ")

    @staticmethod
    def fetchGlobalDimensionsValueForIndexing(globalDimensionGroup):
        """
        Method to fetch the global dimensions and the dimension values.
        :return List of Documents to be indexed
        """
        indexingDocuments = []
        dimension = ""
        logging.info("global dimension group in fetch %s", globalDimensionGroup)
        globalDimensionName = globalDimensionGroup["name"]
        logging.debug("Starting fetch for global dimension: %s", globalDimensionName)
        globalDimensionId = globalDimensionGroup["id"]
        dimensionObjs = globalDimensionGroup["values"]  # dimensional values
        logging.info(
            "Merging dimensions Value percentile with mulitple values in list of dimensionValues"
        )
        for dmObj in dimensionObjs:
            displayValue = ""
            dimension = dmObj["dimension"]
            dataset = dmObj["dataset"]
            datasetId = dmObj["datasetId"]
            res = Utils.getDimensionalValuesForDimension(datasetId, dimension)
            dimensionValues = res.get("data", [])
            for values in dimensionValues:
                if values:
                    logging.info("Dimensional value is %s", values)
                    displayValue = values
                    elasticsearchUniqueId = (
                        str(globalDimensionId)
                        + "_"
                        + str(displayValue)
                        + "_"
                        + str(dataset)
                    )

                    document = {
                        "_id": elasticsearchUniqueId,
                        "globalDimensionValue": str(displayValue).lower(),
                        "globalDimensionDisplayValue": str(displayValue),
                        "globalDimensionName": str(globalDimensionName),
                        "globalDimensionId": globalDimensionId,
                        "dimension": dimension,
                        "dataset": dataset,
                        "datasetId": datasetId,
                    }
                    indexingDocuments.append(document)
                    logging.debug("Document to index: %s", document)

        return indexingDocuments

    @staticmethod
    def indexGlobalDimensionsData(joblogger=None):
        """
        Method to index global dimensions data
        """
        logging.info(
            "****************** Indexing Starts for Global Dimension values **************** "
        )
        response = Utils.getGlobalDimensionForIndex()
        if response["success"]:
            globalDimensions = response.get("data", [])
            logging.debug("Global dimensions Fetched ")

            indexDefinition = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "my_analyzer": {
                                "tokenizer": "my_tokenizer",
                                "filter": ["lowercase"],
                            }
                        },
                        "default_search": {"type": "my_analyzer"},
                        "tokenizer": {
                            "my_tokenizer": {
                                "type": "edge_ngram",
                                "min_gram": 1,
                                "max_gram": 10,
                                "token_chars": ["letter", "digit"],
                            }
                        },
                    }
                },
                "mappings": {
                    "properties": {
                        "globalDimensionId": {"type": "integer"},
                        "globalDimensionDisplayValue": {"type": "keyword"},
                        "globalDimensionValue": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "globalDimensionName": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "dimension": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "dataset": {"type": "text"},
                        "datasetId": {"type": "integer"},
                    }
                },
            }

            indexName = ESIndexingUtils.GLOBAL_DIMENSIONS_INDEX_DATA

            aliasIndex = ESIndexingUtils.initializeIndex(indexName, indexDefinition)
            logging.info("IndexName %s", indexName)
            logging.info("aliasIndex %s", aliasIndex)
            for globalDimensionGroup in globalDimensions:
                logging.info("globaldimensionGroup %s", globalDimensionGroup)
                # globalDimensionGroup is an array
                try:
                    documentsToIndex = (
                        ESIndexingUtils.fetchGlobalDimensionsValueForIndexing(
                            globalDimensionGroup
                        )
                    )

                    ESIndexingUtils.ingestIndex(documentsToIndex, aliasIndex)
                except (Exception) as error:
                    logging.error(str(error))

                    pass

            ESIndexingUtils.deleteOldIndex(indexName, aliasIndex)
            logging.info(
                "****************** Indexing Completed for Global Dimension values **************** "
            )

        else:
            logging.error("Error in fetching global dimensions.")
            raise RuntimeError("Error in fetching global dimensions")

    @staticmethod
    def fetchGlobalDimensionsValueForSearchSuggestionIndexing(globalDimensionGroup):
        """
        Method to fetch the global dimensions and the dimension values.
        :return List of Documents to be indexed
        """
        indexingDocuments = []
        globalDimensionName = globalDimensionGroup["name"]
        logging.debug("Starting fetch for global dimension: %s", globalDimensionName)
        globalDimensionId = globalDimensionGroup["id"]
        dimensionObjs = globalDimensionGroup["values"]  # dimensional values
        logging.info(
            "Merging dimensions Value with mulitple values in list of dimensionValues"
        )
        for dmObj in dimensionObjs:
            displayValue = ""
            dimension = dmObj["dimension"]
            dataset = dmObj["dataset"]
            datasetId = dmObj["datasetId"]
            res = Utils.getDimensionalValuesForDimension(datasetId, dimension)
            dimensionValues = res.get("data", [])
            if dimensionValues:
                for values in dimensionValues:
                    if values:
                        logging.info("Dimensional values is %s", values)

                        displayValue = values
                        elasticsearchUniqueId = (
                            str(globalDimensionId) + "_" + str(displayValue)
                        )

                        document = {
                            "_id": elasticsearchUniqueId,
                            "globalDimensionValue": str(displayValue).lower(),
                            "globalDimensionDisplayValue": str(displayValue),
                            "globalDimensionName": str(globalDimensionName),
                            "globalDimensionId": globalDimensionId,
                            "dataset": dataset,
                            "datasetId": datasetId,
                        }
                        indexingDocuments.append(document)
                        logging.debug("Document to index: %s", document)

        return indexingDocuments

    # Below function is used for search suggestion / To avoid duplicates in search dropdown(Temparory)

    def indexGlobalDimensionsDataForSearchSuggestion(joblogger=None):
        """
        Indexing is being done for dropdown suggestion
        """
        logging.info(
            "*************************** Indexing starts of Global Dimension Values for Search Suggestion **************************"
        )
        response = Utils.getGlobalDimensionForIndex()
        if response["success"]:
            globalDimensions = response.get("data", [])
            logging.debug("Global dimensions: %s", globalDimensions)

            indexDefinition = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "my_analyzer": {
                                "tokenizer": "my_tokenizer",
                                "filter": ["lowercase"],
                            }
                        },
                        "default_search": {"type": "my_analyzer"},
                        "tokenizer": {
                            "my_tokenizer": {
                                "type": "edge_ngram",
                                "min_gram": 1,
                                "max_gram": 10,
                                "token_chars": ["letter", "digit"],
                            }
                        },
                    }
                },
                "mappings": {
                    "properties": {
                        "globalDimensionId": {"type": "integer"},
                        "globalDimensionDisplayValue": {"type": "text"},
                        "globalDimensionValue": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "globalDimensionName": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "dataset": {"type": "text"},
                        "datasetId": {"type": "integer"},
                    }
                },
            }

            indexName = ESIndexingUtils.GLOBAL_DIMENSIONS_INDEX_SEARCH_SUGGESTION_DATA

            aliasIndex = ESIndexingUtils.initializeIndex(indexName, indexDefinition)
            logging.info("IndexName %s", indexName)
            logging.info("aliasIndex %s", aliasIndex)
            for globalDimensionGroup in globalDimensions:
                # globalDimensionGroup is an array
                logging.info("globaldimensionGroup %s", globalDimensionGroup)

                try:
                    documentsToIndex = ESIndexingUtils.fetchGlobalDimensionsValueForSearchSuggestionIndexing(
                        globalDimensionGroup
                    )

                    ESIndexingUtils.ingestIndex(documentsToIndex, aliasIndex)
                except (Exception) as error:
                    logging.error(str(error))

                    pass

            ESIndexingUtils.deleteOldIndex(indexName, aliasIndex)
            logging.info(
                "*************************** Indexing Completed of Global Dimension Values for Search Suggestion **************************"
            )

        else:
            logging.error("Error in fetching global dimensions.")
            raise RuntimeError("Error in fetching global dimensions")

    @staticmethod
    def indexNonGlobalDimensionsDataForSearchSuggestion(joblogger=None):
        """
        Method to index global dimensions data
        """
        from cueSearch.services import GlobalDimensionServices

        logging.info(
            "*************************** Indexing Starts of Non Global Dimension Values for Search Suggestion **************************"
        )

        response = GlobalDimensionServices.nonGlobalDimensionForIndexing()
        if response["success"]:
            datsetDimensions = response.get("data", [])
            logging.debug("Dataset dimensions: %s", datsetDimensions)

            indexDefinition = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "my_analyzer": {
                                "tokenizer": "my_tokenizer",
                                "filter": ["lowercase"],
                            }
                        },
                        "default_search": {"type": "my_analyzer"},
                        "tokenizer": {
                            "my_tokenizer": {
                                "type": "edge_ngram",
                                "min_gram": 1,
                                "max_gram": 10,
                                "token_chars": ["letter", "digit"],
                            }
                        },
                    }
                },
                "mappings": {
                    "properties": {
                        "globalDimensionId": {"type": "text"},
                        "globalDimensionDisplayValue": {"type": "text"},
                        "globalDimensionValue": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "globalDimensionName": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "dimension": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "dataset": {"type": "text"},
                        "datasetId": {"type": "integer"},
                    }
                },
            }

            indexName = (
                ESIndexingUtils.AUTO_GLOBAL_DIMENSIONS_INDEX_DATA_SEARCH_SUGGESTION
            )

            aliasIndex = ESIndexingUtils.initializeIndex(indexName, indexDefinition)
            logging.info("IndexName %s", indexName)
            logging.info("aliasIndex %s", aliasIndex)
            # datsetDimensions is an array
            try:
                documentsToIndex = (
                    ESIndexingUtils.fetchNonGlobalDimensionsValueForIndexing(
                        datsetDimensions
                    )
                )

                ESIndexingUtils.ingestIndex(documentsToIndex, aliasIndex)
            except (Exception) as error:
                logging.error(str(error))

                pass

            ESIndexingUtils.deleteOldIndex(indexName, aliasIndex)
            logging.info(
                "*************************** Indexing Completed of Non Dimensional Values for Search Suggestion **************************"
            )

        else:
            logging.error("Error in fetching global dimensions.")
            raise RuntimeError("Error in fetching global dimensions")

    @staticmethod
    def fetchNonGlobalDimensionsValueForIndexing(datasetDimensions: list):
        """
        Method to fetch the global dimensions and the dimension values.
        :return List of Documents to be indexed
        """
        indexingDocuments = []
        dimension = ""
        globalDimensionName = ""
        globalDimensionId = ""
        dimensionObjs = datasetDimensions
        logging.info(
            "Merging dimensions Value percentile with mulitple values in list of dimensionValues"
        )
        for dmObj in dimensionObjs:
            displayValue = ""
            dimension = dmObj["dimension"]
            dataset = dmObj["dataset"]
            datasetId = dmObj["datasetId"]
            res = Utils.getDimensionalValuesForDimension(datasetId, dimension)
            dimensionValues = res.get("data", [])
            for values in dimensionValues:
                if values:
                    logging.info(
                        " Non global dimensional values %s",
                        values,
                    )
                    displayValue = values
                    globalDimensionId = (
                        str(dimension) + "_" + str(displayValue) + "_" + str(datasetId)
                    )
                    globalDimensionName = str(dataset) + "_" + str(dimension)
                    elasticsearchUniqueId = (
                        str(globalDimensionId)
                        + "_"
                        + str(displayValue)
                        + "_"
                        + str(dataset)
                    )

                    document = {
                        "_id": elasticsearchUniqueId,
                        "globalDimensionValue": str(displayValue).lower(),
                        "globalDimensionDisplayValue": str(displayValue),
                        "globalDimensionName": str(globalDimensionName),
                        "globalDimensionId": globalDimensionId,
                        "dimension": dimension,
                        "dataset": dataset,
                        "datasetId": datasetId,
                    }
                    indexingDocuments.append(document)
        logging.info(
            "Indexing Documents length of non global dimension %s",
            len(indexingDocuments),
        )
        return indexingDocuments

    @staticmethod
    def indexNonGlobalDimensionsData(joblogger=None):
        """
        Method to index Non global dimensions data
        """
        from cueSearch.services import GlobalDimensionServices

        logging.info(
            "*************************** Indexing Starts of Non Global Dimension Data **************************"
        )

        response = GlobalDimensionServices.nonGlobalDimensionForIndexing()
        if response["success"]:
            datsetDimensions = response.get("data", [])
            logging.debug("Dataset dimensions: %s", datsetDimensions)

            indexDefinition = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "my_analyzer": {
                                "tokenizer": "my_tokenizer",
                                "filter": ["lowercase"],
                            }
                        },
                        "default_search": {"type": "my_analyzer"},
                        "tokenizer": {
                            "my_tokenizer": {
                                "type": "edge_ngram",
                                "min_gram": 1,
                                "max_gram": 10,
                                "token_chars": ["letter", "digit"],
                            }
                        },
                    }
                },
                "mappings": {
                    "properties": {
                        "globalDimensionId": {"type": "text"},
                        "globalDimensionDisplayValue": {"type": "keyword"},
                        "globalDimensionValue": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "globalDimensionName": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "dimension": {
                            "type": "text",
                            "search_analyzer": "my_analyzer",
                            "analyzer": "my_analyzer",
                            "fields": {
                                "ngram": {"type": "text", "analyzer": "my_analyzer"}
                            },
                        },
                        "dataset": {"type": "text"},
                        "datasetId": {"type": "integer"},
                    }
                },
            }

            indexName = ESIndexingUtils.AUTO_GLOBAL_DIMENSIONS_INDEX_DATA

            aliasIndex = ESIndexingUtils.initializeIndex(indexName, indexDefinition)
            logging.info("IndexName %s", indexName)
            logging.info("aliasIndex %s", aliasIndex)
            # datsetDimensions is an array
            try:
                documentsToIndex = (
                    ESIndexingUtils.fetchNonGlobalDimensionsValueForIndexing(
                        datsetDimensions
                    )
                )

                ESIndexingUtils.ingestIndex(documentsToIndex, aliasIndex)
            except (Exception) as error:
                logging.error(str(error))

                pass

            ESIndexingUtils.deleteOldIndex(indexName, aliasIndex)
            logging.info(
                "*************************** Indexing Completed of Non Dimensional Data **************************"
            )

        else:
            logging.error("Error in fetching global dimensions.")
            raise RuntimeError("Error in fetching global dimensions")
