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
from cueSearch.elasticSearch import ESIndexingUtils, Utils, ESQueryingUtils
import logging
from cueSearch.services import GlobalDimensionServices


@pytest.mark.django_db(transaction=True)
def test_indexGlobalDimensionsDataForSearchSuggestion(client, mocker):
    """
    Method for test index global dimension data for suggestion
    """
    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.runAllIndexDimension",
        new=mock.MagicMock(autospec=True, return_value=True),
    )
    mockResponse.start()
    connection = mixer.blend("dataset.connection")
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
    assert response.data["success"]

    # create dimension for testing
    dataset = Dataset.objects.all()[0]
    path = reverse("globalDimensionCreate")
    gd_data = {
        "name": "test01",
        "dimensionalValues": [
            {
                "datasetId": dataset.id,
                "dataset": "Returns",
                "dimension": "WarehouseCode",
                "published": True,
            }
        ],
    }
    response = client.post(path, gd_data, content_type="application/json")

    # Getting global dimension id
    temp = GlobalDimensionServices.getGlobalDimensions()
    globalDimensionId = temp.data[0]["values"][0]["id"]
    # Publishing global dimension by id
    path = reverse("pubGlobalDimension")
    payload = {"id": globalDimensionId, "published": True}
    response = client.post(path, payload)

    res = {"success": True, "data": ["adidas", "nike"]}
    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.utils.Utils.getDimensionalValuesForDimension",
        new=mock.MagicMock(autospec=True, return_value=res),
    )
    ESIndexingUtils.indexGlobalDimensionsDataForSearchSuggestion()
    mockResponse.stop()
    query = "n"
    searchResults = ESQueryingUtils.findGlobalDimensionResultsForSearchSuggestion(
        query=query
    )


@pytest.mark.django_db(transaction=True)
def test_indexNonGlobalDimensionsDataForSearchSuggestion(client, mocker):
    """
    Method for test non global dimension data for suggestion
    """
    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.runAllIndexDimension",
        new=mock.MagicMock(autospec=True, return_value=True),
    )
    mockResponse.start()
    connection = mixer.blend("dataset.connection")
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
    assert response.data["success"]

    res = {"success": True, "data": ["adidas", "nike"]}
    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.utils.Utils.getDimensionalValuesForDimension",
        new=mock.MagicMock(autospec=True, return_value=res),
    )
    temp = ESIndexingUtils.indexNonGlobalDimensionsDataForSearchSuggestion()
    mockResponse.stop()
    query = "adidas"
    respQuery = ESQueryingUtils.findNonGlobalDimensionResultsForSearchSuggestion(
        query=query
    )
    # breakpoint()


@pytest.mark.django_db(transaction=True)
def test_indexGlobalDimensionName(client, mocker):
    """
    Method for test global dimension name
    """
    # response = ESIndexingUtils.indexGlobalDimensionName()
    # breakpoint()
    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.runAllIndexDimension",
        new=mock.MagicMock(autospec=True, return_value=True),
    )
    mockResponse.start()
    connection = mixer.blend("dataset.connection")
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
    assert response.data["success"]

    # create dimension for testing
    dataset = Dataset.objects.all()[0]
    path = reverse("globalDimensionCreate")
    gd_data = {
        "name": "test01",
        "dimensionalValues": [
            {
                "datasetId": dataset.id,
                "dataset": "Returns",
                "dimension": "WarehouseCode",
                "published": True,
            }
        ],
    }
    response = client.post(path, gd_data, content_type="application/json")

    # Getting global dimension id
    temp = GlobalDimensionServices.getGlobalDimensions()
    globalDimensionId = temp.data[0]["values"][0]["id"]
    # Publishing global dimension by id
    path = reverse("pubGlobalDimension")
    payload = {"id": globalDimensionId, "published": True}
    response = client.post(path, payload)

    ESIndexingUtils.indexGlobalDimensionName()
    searchResults = ESQueryingUtils.findGlobalDimensionNames("City")


@pytest.mark.django_db(transaction=True)
def test_indexGlobalDimensionsData(client, mocker):
    """
    Method for test index global dimension data
    """
    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.runAllIndexDimension",
        new=mock.MagicMock(autospec=True, return_value=True),
    )
    mockResponse.start()
    connection = mixer.blend("dataset.connection")
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
    assert response.data["success"]

    # create dimension for testing
    dataset = Dataset.objects.all()[0]
    path = reverse("globalDimensionCreate")
    gd_data = {
        "name": "test01",
        "dimensionalValues": [
            {
                "datasetId": dataset.id,
                "dataset": "Returns",
                "dimension": "WarehouseCode",
                "published": True,
            }
        ],
    }
    response = client.post(path, gd_data, content_type="application/json")

    # Getting global dimension id
    temp = GlobalDimensionServices.getGlobalDimensions()
    globalDimensionId = temp.data[0]["values"][0]["id"]
    # Publishing global dimension by id
    path = reverse("pubGlobalDimension")
    payload = {"id": globalDimensionId, "published": True}
    response = client.post(path, payload)

    ESIndexingUtils.indexGlobalDimensionsData()
