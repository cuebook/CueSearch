from http import client
import re
import pytest
from unittest import mock
from django.urls import reverse
import unittest
from django.test import TestCase,Client
from rest_framework.test import APITestCase,APIClient
from mixer.backend.django import mixer
from dataset.models import Dataset


@pytest.mark.django_db(transaction=True)
def test_createGlobalDimension(client,mocker):
    '''
    Test case for creating global dimension
    '''
    #create demo data for global dimension
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
        "isNonRollup": False
    }
    response = client.post(path, data=data, content_type="application/json")
    assert response.data['success']

    #create dimension for testing
    dataset = Dataset.objects.all()[0]
    path = reverse('globalDimensionCreate')
    gd_data = {
        'name': 'test', 
        'dimensionalValues': [{'datasetId': dataset.id,"dataset":"Returns","dimension":"WarehouseCode"}]
        }
    
    response = client.post(path,gd_data, content_type="application/json")
    assert response.data["success"]
    assert response.status_code == 200
    





