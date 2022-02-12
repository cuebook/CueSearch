# from builtins import breakpoint
# from http import client
# from logging import exception
# import re
# from urllib import response
# import pytest
# from unittest import mock
# from django.urls import reverse
# import unittest
# from django.test import TestCase, Client
# from rest_framework.test import APITestCase, APIClient
# from mixer.backend.django import mixer
# from dataset.models import Dataset
# from cueSearch.elasticSearch import ESQueryingUtils
# from django.dispatch import receiver


# def createTestingDataset(client, mocker):
#     """
#     Method to create test dataset
#     """
#     mockResponse = mocker.patch(
#         "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.runAllIndexDimension",
#         new=mock.MagicMock(autospec=True, return_value=True),
#     )
#     mockResponse.start()
#     connection = mixer.blend("dataset.connection")
#     path = reverse("createDataset")
#     data = {
#         "name": "demo_dataset",
#         "sql": "SELECT * from TEST_TABLE",
#         "connectionId": connection.id,
#         "metrics": ["Amount", "Quantity"],
#         "dimensions": ["Category", "Region"],
#         "timestamp": "CreatedAt",
#         "granularity": "day",
#         "isNonRollup": False,
#     }
#     datasetResponse = client.post(path, data=data, content_type="application/json")
#     return datasetResponse


# def createGlobalDimension(client, mocker):
#     """
#     Method to create a global dimension for testing
#     """
#     dataset = Dataset.objects.all()[0]
#     path = reverse("globalDimensionCreate")
#     globalDimension = {
#         "name": "test01",
#         "dimensionalValues": [
#             {
#                 "datasetId": dataset.id,
#                 "dataset": "Returns",
#                 "dimension": "WarehouseCode",
#                 "published": True,
#             }
#         ],
#     }
#     globalDimsResponse = client.post(
#         path, globalDimension, content_type="application/json"
#     )
#     return globalDimsResponse


# #     ========================  Testcases area  ==============================


# @pytest.mark.django_db(transaction=True)
# def test_findGlobalDimensionResults(client, mocker):

#     # Create test dataset
#     testData = createTestingDataset(client, mocker)
#     # Create global dimension for testing
#     globalDimension = createGlobalDimension(client, mocker)
#     query = "AD"
#     result = ESQueryingUtils.findGlobalDimensionResults(query=query)

#     expectedResult = [
#         {
#             "value": "AD",
#             "dimension": "DeliveryRegion",
#             "globalDimensionName": "Data",
#             "user_entity_identifier": "Data",
#             "id": 8,
#             "dataset": "Test data",
#             "datasetId": 1,
#             "type": "GLOBALDIMENSION",
#         }
#     ]
#     assert result == expectedResult


# @pytest.mark.django_db(transaction=True)
# def test_findGlobalDimensionResultsForSearchSuggestion(client, mocker):

#     # Create test dataset
#     testData = createTestingDataset(client, mocker)
#     # Create global dimension for testing
#     globalDimension = createGlobalDimension(client, mocker)

#     path = reverse("globalDimension")
#     response = client.get(path)
#     query = "AP"
#     result = ESQueryingUtils.findGlobalDimensionResultsForSearchSuggestion(query=query)
#     expectedResult = [
#         {
#             "value": "AP",
#             "user_entity_identifier": "Data",
#             "id": 8,
#             "type": "GLOBALDIMENSION",
#         }
#     ]
#     assert result == expectedResult


# @pytest.mark.django_db(transaction=True)
# def test_findNonGlobalDimensionResultsForSearchSuggestion(client, mocker):
#     # Create test dataset
#     testData = createTestingDataset(client, mocker)

#     # Create global dimension for testing
#     globalDimension = createGlobalDimension(client, mocker)

#     path = reverse("globalDimension")
#     response = client.get(path)
#     query = "ADARA"
#     result = ESQueryingUtils.findNonGlobalDimensionResultsForSearchSuggestion(
#         query=query
#     )

#     expectedResult = [
#         {
#             "value": "ADARA",
#             "user_entity_identifier": "Test data_Brand",
#             "id": "Brand_ADARA_1",
#             "datasetId": 1,
#             "globalDimensionId": "Brand_ADARA_1",
#             "type": "DATASETDIMENSION",
#         }
#     ]
#     assert result == expectedResult


# @pytest.mark.django_db(transaction=True)
# def test_findNonGlobalDimensionResults(client, mocker):

#     # Create test dataset
#     testData = createTestingDataset(client, mocker)
#     # Create global dimension for testing
#     globalDimension = createGlobalDimension(client, mocker)
#     query = "ADARA"
#     result = ESQueryingUtils.findNonGlobalDimensionResults(query=query)

#     expectedResult = [
#         {
#             "value": "ADARA",
#             "dimension": "Brand",
#             "globalDimensionName": "Test data_Brand",
#             "user_entity_identifier": "Test data_Brand",
#             "id": "Brand_ADARA_1",
#             "dataset": "Test data",
#             "datasetId": 1,
#             "type": "DATASETDIMENSION",
#         }
#     ]
#     assert result == expectedResult
