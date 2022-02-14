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
    ESIndexingUtils.deleteAllIndex()
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

    # create dimension for testing
    dataset = Dataset.objects.get(id=1)
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
    assert response.data["success"] == True
    assert response.status_code == 200

    globalDimsId = GlobalDimensionServices.getGlobalDimensions()
    globalDimensionId = globalDimsId.data[0]["values"][0]["id"]

    # Publishing global dimension by id
    path = reverse("pubGlobalDimension")
    payload = {"id": globalDimensionId, "published": True}
    response = client.post(path, payload)
    mockResponse.stop()

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
    count = 0
    while not result:
        count += 1

        result = ESQueryingUtils.findGlobalDimensionResultsForSearchSuggestion(
            query=query
        )
        if count == 10:
            result = []
            return result
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


@pytest.mark.django_db(transaction=True)
def testIndexGlobalDimensinData(client, mocker):
    """Method to test index global dimension data"""
    ESIndexingUtils.deleteAllIndex()
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

    # create dimension for testing
    dataset = Dataset.objects.get(id=1)
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
    assert response.data["success"] == True
    assert response.status_code == 200

    globalDimsId = GlobalDimensionServices.getGlobalDimensions()
    globalDimensionId = globalDimsId.data[0]["values"][0]["id"]

    # Publishing global dimension by id
    path = reverse("pubGlobalDimension")
    payload = {"id": globalDimensionId, "published": True}
    response = client.post(path, payload)
    mockResponse.stop()

    ##################### Global dimension data index ######################
    # Creating a index value
    res = {"success": True, "data": ["TestData", "TestDataOne"]}

    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.utils.Utils.getDimensionalValuesForDimension",
        new=mock.MagicMock(autospec=True, return_value=res),
    )
    ESIndexingUtils.indexGlobalDimensionsData()
    mockResponse.stop()
    query = "TestData"
    result = ESQueryingUtils.findGlobalDimensionResults(query=query)
    count = 0
    while not result:
        count += 1
        result = ESQueryingUtils.findGlobalDimensionResults(query=query)

        if count == 10:
            result = []
            return result

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


@pytest.mark.django_db(transaction=True)
def testNonGlobalDimensionDataIndex(client, mocker):
    """Method to test non global dimension index"""
    ESIndexingUtils.deleteAllIndex()

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

    # create dimension for testing
    dataset = Dataset.objects.get(id=1)
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
    assert response.data["success"] == True
    assert response.status_code == 200

    globalDimsId = GlobalDimensionServices.getGlobalDimensions()
    globalDimensionId = globalDimsId.data[0]["values"][0]["id"]

    # Publishing global dimension by id
    path = reverse("pubGlobalDimension")
    payload = {"id": globalDimensionId, "published": True}
    response = client.post(path, payload)
    mockResponse.stop()

    ################################ Global dimension data index #################

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
    count = 0
    while not result:
        count += 1
        result = ESQueryingUtils.findNonGlobalDimensionResultsForSearchSuggestion(
            query=query
        )

        if count == 10:
            result = []
            return result

    expectedResult = [
        {
            "value": "TestData",
            "user_entity_identifier": "Test data_Brand",
            "id": "Brand_TestData_1",
            "datasetId": testDataset.id,
            "globalDimensionId": "Brand_TestData_1",
            "type": "DATASETDIMENSION",
        },
        {
            "value": "TestData",
            "user_entity_identifier": "Test data_WarehouseCode",
            "id": "WarehouseCode_TestData_1",
            "datasetId": testDataset.id,
            "globalDimensionId": "WarehouseCode_TestData_1",
            "type": "DATASETDIMENSION",
        },
        {
            "value": "TestDataOne",
            "user_entity_identifier": "Test data_Brand",
            "id": "Brand_TestDataOne_1",
            "datasetId": testDataset.id,
            "globalDimensionId": "Brand_TestDataOne_1",
            "type": "DATASETDIMENSION",
        },
        {
            "value": "TestDataOne",
            "user_entity_identifier": "Test data_WarehouseCode",
            "id": "WarehouseCode_TestDataOne_1",
            "datasetId": testDataset.id,
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
            "datasetId": testDataset.id,
            "type": "DATASETDIMENSION",
        },
        {
            "value": "TestData",
            "dimension": "WarehouseCode",
            "globalDimensionName": "Test data_WarehouseCode",
            "user_entity_identifier": "Test data_WarehouseCode",
            "id": "WarehouseCode_TestData_1",
            "dataset": "Test data",
            "datasetId": testDataset.id,
            "type": "DATASETDIMENSION",
        },
    ]
    result = ESQueryingUtils.findNonGlobalDimensionResults(query=query)
    count = 0
    while not result:
        count += 1
        result = ESQueryingUtils.findNonGlobalDimensionResults(query=query)

        if count == 10:
            result = []
            return result

    assert result == expectedResults
    ################################ Delete all indexes ##############


def testRunAllIndexing(client, mocker):

    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.indexGlobalDimensionsDataForSearchSuggestion",
        new=mock.MagicMock(autospec=True, return_value=True),
    )
    mockResponse.start()
    mockResponse1 = mocker.patch(
        "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.indexGlobalDimensionsData",
        new=mock.MagicMock(autospec=True, return_value=True),
    )
    mockResponse1.start()
    mockResponse2 = mocker.patch(
        "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.indexNonGlobalDimensionsDataForSearchSuggestion",
        new=mock.MagicMock(autospec=True, return_value=True),
    )
    mockResponse2.start()

    ESIndexingUtils.runAllIndexDimension()

    mockResponse.stop()
    mockResponse1.stop()
    mockResponse2.stop()
