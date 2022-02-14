import pytest
import pandas as pd
from unittest import mock
from mixer.backend.django import mixer
from django.urls import reverse
from dataset.models import Dataset
from cueSearch.elasticSearch import Utils


@pytest.mark.django_db(transaction=True)
def testGetGlobalDimensionForIndex(client, mocker):
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
    mockResponse.start()
    path = reverse("globalDimensionCreate")
    gd_data = {
        "name": "test01",
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
    assert response.data["success"]
    assert response.status_code == 200
    # Getting global dimension id
    path = reverse("globalDimension")
    response = client.get(path)
    globalDim_id = response.json().get("data", [])
    globalDim_id = globalDim_id[0]["id"]
    # published global dimension
    path = reverse("pubGlobalDimension")
    payload = {"id": globalDim_id, "published": True}
    response = client.post(path, payload)
    assert response.data["success"] == True
    assert response.status_code == 200

    res = Utils.getGlobalDimensionForIndex()
    assert res["success"] == True
    assert res["data"][0]["values"][0]["dimension"] == "WarehouseCode"
    assert res["data"][0]["values"][0]["dataset"] == "demo_dataset"
    datasetId = res["data"][0]["values"][0]["datasetId"]
    dimension = res["data"][0]["values"][0]["dimension"]

    res = Utils.getDimensionalValuesForDimension(datasetId, dimension)
    res["success"] == False
    res["data"] == []

    df = pd.DataFrame(columns=[dimension])
    mockResponse = mocker.patch(
        "access.data.Data.fetchDatasetDataframe",
        new=mock.MagicMock(autospec=True, return_value=df),
    )
    mockResponse.start()
    res = Utils.getDimensionalValuesForDimension(datasetId, dimension)
    mockResponse.stop()
    assert res["data"] == []
    assert res["success"] == True
