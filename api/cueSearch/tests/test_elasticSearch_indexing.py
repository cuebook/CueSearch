import pytest
from unittest import mock, result
from django.urls import reverse
from mixer.backend.django import mixer
from dataset.models import Dataset
from cueSearch.elasticSearch import ESQueryingUtils
from cueSearch.elasticSearch import ESIndexingUtils
from cueSearch.services import GlobalDimensionServices
from cueSearch.elasticSearch.utils import Utils


@pytest.mark.django_db(transaction=True)
def test_elastic_search_indexing(client, mocker):
    """
    Method to create test dataset
    """
    connection = mixer.blend("dataset.connection")
    testDataset = mixer.blend(
        "dataset.dataset",
        name="orders",
        id=1,
        dimensions='["Brand", "Color", "State"]',
        metrics='["Orders", "OrderAmount", "OrderQuantity"]',
        granularity="day",
        timestampColumn="TestDate",
        sql="Select * from testTable",
    )
    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.runAllIndexDimension",
        new=mock.MagicMock(autospec=True, return_value=True),
    )
    mockResponse.start()
    path = reverse("createDataset")
    data = {
        "name": "demo_dataset",
        "sql": "SELECT * from TEST_TABLE",
        "connectionId": connection.id,
        "metrics": ["Amount", "Quantity"],
        "dimensions": ["Category", "Region"],
        "timestamp": "CreatedAt",
        "granularity": "day",
        "isNonRollup": False,
    }
    response = client.post(path, data=data, content_type="application/json")
    mockResponse.stop()

    # create dimension for testing
    dataset = Dataset.objects.all()[0]
    mockResponse.start()
    path = reverse("globalDimensionCreate")
    gd_data = {
        "name": "test",
        "dimensionalValues": [
            {
                "datasetId": dataset.id,
                "dataset": "Returns",
                "dimension": "WarehouseCode",
            }
        ],
    }
    response = client.post(path, gd_data, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"] == True
    assert response.status_code == 200

    globalDimsId = GlobalDimensionServices.getGlobalDimensions()
    globalDimensionId = globalDimsId.data[0]["values"][0]["id"]

    # Publishing global dimension by id
    path = reverse("pubGlobalDimension")
    payload = {"id": globalDimensionId, "published": True}
    response = client.post(path, payload)

    # Testing the indexing of global dimension data for suggestion

    # Creating a index value
    res = {"success": True, "data": ["TestData", "TestDataOne"]}

    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.utils.Utils.getDimensionalValuesForDimension",
        new=mock.MagicMock(autospec=True, return_value=res),
    )
    ESIndexingUtils.indexGlobalDimensionsDataForSearchSuggestion()
    mockResponse.stop()
    # Deeply testing of global dimension indexing
    dataIndex = Utils.getDimensionalValuesForDimension(dataset.id, "Brand")
    assert dataIndex["data"] == ["TestData", "TestDataOne"]

    query = "TestData"
    result = ESQueryingUtils.findGlobalDimensionResultsForSearchSuggestion(query=query)
    expectedResult = [
        {
            "value": "TestData",
            "user_entity_identifier": "test",
            "id": globalDimensionId,
            "type": "GLOBALDIMENSION",
        },
        {
            "value": "TestDataOne",
            "user_entity_identifier": "test",
            "id": globalDimensionId,
            "type": "GLOBALDIMENSION",
        },
    ]

    assert result == expectedResult

    ######################################################### Deletion of Indexed search suggestion data ###############################################
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
                    "fields": {"ngram": {"type": "text", "analyzer": "my_analyzer"}},
                },
                "globalDimensionName": {
                    "type": "text",
                    "search_analyzer": "my_analyzer",
                    "analyzer": "my_analyzer",
                    "fields": {"ngram": {"type": "text", "analyzer": "my_analyzer"}},
                },
                "dataset": {"type": "text"},
                "datasetId": {"type": "integer"},
            }
        },
    }

    indexName = ESIndexingUtils.GLOBAL_DIMENSIONS_INDEX_SEARCH_SUGGESTION_DATA

    aliasIndex = ESIndexingUtils.initializeIndex(indexName, indexDefinition)
    ESIndexingUtils.deleteOldIndex(indexName, aliasIndex)

    ###################################################################### Deletion complete for global dimension search suggestion index ################################################

    ##################### Global dimension data index ######################
    # Creating a index value
    res = {"success": True, "data": ["TestData", "TestDataOne"]}

    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.utils.Utils.getDimensionalValuesForDimension",
        new=mock.MagicMock(autospec=True, return_value=res),
    )
    ESIndexingUtils.indexGlobalDimensionsData()
    mockResponse.stop()
    result = ESQueryingUtils.findGlobalDimensionResults(query=query)
    expectedResults = [
        {
            "value": "TestData",
            "dimension": "WarehouseCode",
            "globalDimensionName": "test",
            "user_entity_identifier": "test",
            "id": globalDimensionId,
            "dataset": "orders",
            "datasetId": testDataset.id,
            "type": "GLOBALDIMENSION",
        }
    ]
    assert result == expectedResults

    ################################ Global dimension data index #################
    ######################### Deletion of Global dimension index name ##############
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
                    "fields": {"ngram": {"type": "text", "analyzer": "my_analyzer"}},
                },
                "globalDimensionName": {
                    "type": "text",
                    "search_analyzer": "my_analyzer",
                    "analyzer": "my_analyzer",
                    "fields": {"ngram": {"type": "text", "analyzer": "my_analyzer"}},
                },
                "dimension": {
                    "type": "text",
                    "search_analyzer": "my_analyzer",
                    "analyzer": "my_analyzer",
                    "fields": {"ngram": {"type": "text", "analyzer": "my_analyzer"}},
                },
                "dataset": {"type": "text"},
                "datasetId": {"type": "integer"},
            }
        },
    }

    indexName = ESIndexingUtils.GLOBAL_DIMENSIONS_INDEX_DATA

    aliasIndex = ESIndexingUtils.initializeIndex(indexName, indexDefinition)
    ESIndexingUtils.deleteOldIndex(indexName, aliasIndex)

    ##################################### Deletion completed ########################################

    listToIndex = [
        {"dataset": "Test data", "datasetId": 1, "dimension": "Brand"},
        {"dataset": "Test data", "datasetId": 1, "dimension": "WarehouseCode"},
    ]
    res = {"success": True, "data": listToIndex}

    mockResponse = mocker.patch(
        "cueSearch.services.globalDimension.GlobalDimensionServices.nonGlobalDimensionForIndexing",
        new=mock.MagicMock(autospec=True, return_value=res),
    )
    mockResponse.start()
    ESIndexingUtils.indexNonGlobalDimensionsDataForSearchSuggestion()
    mockResponse.stop()

    query = "TestData"
    result = ESQueryingUtils.findNonGlobalDimensionResultsForSearchSuggestion(
        query=query
    )

    expectedResult = [
        {
            "value": "TestData",
            "user_entity_identifier": "Test data_Brand",
            "id": "Brand_TestData_1",
            "datasetId": 1,
            "globalDimensionId": "Brand_TestData_1",
            "type": "DATASETDIMENSION",
        },
        {
            "value": "TestData",
            "user_entity_identifier": "Test data_WarehouseCode",
            "id": "WarehouseCode_TestData_1",
            "datasetId": 1,
            "globalDimensionId": "WarehouseCode_TestData_1",
            "type": "DATASETDIMENSION",
        },
        {
            "value": "TestDataOne",
            "user_entity_identifier": "Test data_Brand",
            "id": "Brand_TestDataOne_1",
            "datasetId": 1,
            "globalDimensionId": "Brand_TestDataOne_1",
            "type": "DATASETDIMENSION",
        },
        {
            "value": "TestDataOne",
            "user_entity_identifier": "Test data_WarehouseCode",
            "id": "WarehouseCode_TestDataOne_1",
            "datasetId": 1,
            "globalDimensionId": "WarehouseCode_TestDataOne_1",
            "type": "DATASETDIMENSION",
        },
    ]
    assert result == expectedResult

    expectedResults = [
        {
            "value": "TestData",
            "dimension": "Brand",
            "globalDimensionName": "Test data_Brand",
            "user_entity_identifier": "Test data_Brand",
            "id": "Brand_TestData_1",
            "dataset": "Test data",
            "datasetId": 1,
            "type": "DATASETDIMENSION",
        },
        {
            "value": "TestData",
            "dimension": "WarehouseCode",
            "globalDimensionName": "Test data_WarehouseCode",
            "user_entity_identifier": "Test data_WarehouseCode",
            "id": "WarehouseCode_TestData_1",
            "dataset": "Test data",
            "datasetId": 1,
            "type": "DATASETDIMENSION",
        },
    ]
    result = ESQueryingUtils.findNonGlobalDimensionResults(query=query)
    assert result == expectedResults

    ####################################################### Deletion of Non global dimension search suggestion ######################################
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
                    "fields": {"ngram": {"type": "text", "analyzer": "my_analyzer"}},
                },
                "globalDimensionName": {
                    "type": "text",
                    "search_analyzer": "my_analyzer",
                    "analyzer": "my_analyzer",
                    "fields": {"ngram": {"type": "text", "analyzer": "my_analyzer"}},
                },
                "dimension": {
                    "type": "text",
                    "search_analyzer": "my_analyzer",
                    "analyzer": "my_analyzer",
                    "fields": {"ngram": {"type": "text", "analyzer": "my_analyzer"}},
                },
                "dataset": {"type": "text"},
                "datasetId": {"type": "integer"},
            }
        },
    }

    indexName = ESIndexingUtils.AUTO_GLOBAL_DIMENSIONS_INDEX_DATA

    aliasIndex = ESIndexingUtils.initializeIndex(indexName, indexDefinition)
    ESIndexingUtils.deleteOldIndex(indexName, aliasIndex)

    ######################################################### Deletion completed for Auto Global Dimension Index #########################################
