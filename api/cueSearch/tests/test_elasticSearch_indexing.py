from builtins import breakpoint
from http import client
from logging import exception
import re
from urllib import response
import pytest
from unittest import mock
from django.urls import reverse
import unittest
from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient
from mixer.backend.django import mixer
from dataset.models import Dataset
from cueSearch.elasticSearch import ESQueryingUtils,ESIndexingUtils
from django.dispatch import receiver


@pytest.mark.django_db(transaction=True)
def test_elastic_search_indexing(client,mocker):
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
    
    res = {
        "success": True, 
        "data": ["puma", "adidas","HRX"]
        }
    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.utils.Utils.getDimensionalValuesForDimension",
        new=mock.MagicMock(autospec=True, return_value=res),
    )
    mockResponse.start()
    ESIndexingUtils.indexGlobalDimensionsDataForSearchSuggestion()
    mockResponse.stop()

    query='MH'
    result = ESQueryingUtils.findGlobalDimensionResults(
                query=query
            )

    expectedResult = [
                { 
                    'value': 'MH',
                    'dimension': 'DeliveryRegion', 
                    'globalDimensionName': 'Data', 
                    'user_entity_identifier': 'Data', 
                    'id': 8, 'dataset': 'Test data', 
                    'datasetId': 1, 
                    'type': 'GLOBALDIMENSION'
                }
            ]
    breakpoint()
    assert result == expectedResult

    



