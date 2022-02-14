from cProfile import label
import pytest
import unittest
import pandas as pd
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from dataset.services.querys import Querys
from dataset.services import Datasets, Connections


@pytest.mark.django_db(transaction=True)
def test_query(client, mocker):
    """
    Test case for connections
    """
    connectionType = mixer.blend('dataset.connectionType', label='druid', name='Druid')
    connection = mixer.blend('dataset.connection', name='druid_test_data', description='Test', connectionType=connectionType)
    connectionParam = mixer.blend('dataset.connectionParam', name="test_druid_param", label='test_druid_param', connectionType=connectionType)


    payload = {
    "sql": "SELECT DATE_TRUNC('DAY', __time) as ReturnDate,\nDeliveryRegionCode as DeliveryRegion, P_BRANDCODE as Brand, WarehouseCode,\nSUM(\"count\") as ReturnEntries, sum(P_FINALREFUNDAMOUNT) as RefundAmount\nFROM RETURNENTRY\nWHERE __time >= CURRENT_TIMESTAMP - INTERVAL '13' MONTH \nGROUP BY 1, 2, 3, 4\nORDER BY 1",
    "connectionId": connection.id
    }
    df = pd.DataFrame()
    mockResponse = mocker.patch(
        "access.data.Data.runQueryOnConnection",
        new=mock.MagicMock(autospec=True, return_value=df),
    )
    path = reverse('querys')
    response = client.post(path,payload, content_type="application/json")
    mockResponse.stop()
    assert response.status_code == 200
    assert response.json()['success'] == True

    df = []
    mockResponse = mocker.patch(
        "access.data.Data.runQueryOnConnection",
        new=mock.MagicMock(autospec=True, return_value=df),
    )
    path = reverse('querys')
    response = client.post(path,payload, content_type="application/json")
    mockResponse.stop()
  
    assert response.status_code == 200
    assert response.json()['success'] == False
