from builtins import breakpoint
from http import client
import re
import pytest
from unittest import mock
from django.urls import reverse
import unittest
from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient
from mixer.backend.django import mixer
from dataset.models import Dataset
from unittest import mock

# Working condition


@pytest.mark.django_db(transaction=True)
def test_updateGlobalDimension(client, mocker):
    """
    Test case for update global dimension
    """
    # create demo data for global dimension
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
    # get global dimension
    path = reverse("globalDimension")
    response = client.get(path)
    assert response.data["data"][0]["id"] == dataset.id
    assert response.data["success"]
    assert response.status_code == 200

    # Getting global dimension id
    path = reverse("globalDimension")
    response = client.get(path)
    globalDim_id = response.json().get("data", [])
    globalDim_id = globalDim_id[0]["id"]

    # Updating the exsisting global dimension by Id
    path = reverse("updateGlobalDimension", kwargs={"id": globalDim_id})
    mockResponse.start()
    payload = {"name": "test", "dimensionalValues": [], "published": True}

    response = client.post(path, payload)
    mockResponse.stop()
    assert response.data["success"] == True
    assert response.status_code == 200
