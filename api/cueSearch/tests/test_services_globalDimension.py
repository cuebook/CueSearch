import pytest
from unittest import mock
from django.urls import reverse
from mixer.backend.django import mixer
from dataset.models import Dataset
from cueSearch.services import GlobalDimensionServices


@pytest.mark.django_db(transaction=True)
def testGlobalDimension(client, mocker):
    """
    Method to test global dimension services
    """
    # creating a demo data
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

    # Creating a global dimension for testing
    dataset = Dataset.objects.all()[0]
    mockResponse.start()
    path = reverse("globalDimensionCreate")
    globalDimension = {
        "name": "test01",
        "dimensionalValues": [
            {
                "datasetId": dataset.id,
                "dataset": "Returns",
                "dimension": "WarehouseCode",
            }
        ],
    }
    response = client.post(path, globalDimension, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"]
    assert response.status_code == 200

    # Getting the created global dimension
    path = reverse("globalDimension")
    response = client.get(path)
    result = response.json()
    expectedResults = globalDimension["dimensionalValues"][0]["dimension"]

    assert response.data["success"]
    assert result["data"][0]["values"][0]["dimension"] == expectedResults

    # Deeply testing of global dimension
    mockResponse.start()
    path = reverse("globalDimensionCreate")
    globalDimension = {
        "name": "test02",
        "dimensionalValues": [
            {
                "datasetId": dataset.id,
                "dataset": "Returns",
                "dimension": "Brands",
            }
        ],
    }
    response = client.post(path, globalDimension, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"]

    # Checking the create global dimension api exception
    mockResponse.start()
    path = reverse("globalDimensionCreate")
    globalDimension = {}
    response = client.post(path, globalDimension, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"] == False
    assert response.json()["message"] == "Global Dimension name already exists"

    # Getting the existing all global dimension id
    mockResponse.start()
    path = reverse("globalDimension")
    response = client.get(path, content_type="application/json")
    mockResponse.stop()
    assert len(response.json()["data"]) == 2
    assert response.json()["data"][0]["values"][0]["dimension"] == "Brands"
    assert response.json()["data"][1]["values"][0]["dimension"] == "WarehouseCode"
    assert response.json()["data"][0]["published"] == False

    # Now publishing the global dimension
    GlobalDimsId = response.json()["data"][0]["id"]
    mockResponse.start()
    path = reverse("pubGlobalDimension")
    payload = {"id": GlobalDimsId, "published": True}
    response = client.post(path, payload, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"] == True

    # Checking the published global dimension
    mockResponse.start()
    path = reverse("globalDimension")
    response = client.get(path, content_type="application/json")
    mockResponse.stop()
    assert response.json()["data"][0]["published"] == True
    assert response.json()["data"][1]["published"] == False

    # checking the publishing api exception without id error
    mockResponse.start()
    path = reverse("pubGlobalDimension")
    payload = {"id": [], "published": True}
    response = client.post(path, payload, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"] == False
    assert response.json()["message"] == "Id is mandatory"

    # checking the publishing api exception with id error
    mockResponse.start()
    path = reverse("pubGlobalDimension")
    payload = {"id": 277, "published": True}
    response = client.post(path, payload, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"] == False
    assert response.json()["message"] == "Error occured while updating global dimension"

    # Deleting the global dimension called Brands
    mockResponse.start()
    path = reverse("global-dimension-delete", kwargs={"id": GlobalDimsId})
    response = client.delete(path, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"] == True
    assert response.status_code == 200

    # Checking the deleted global dimension
    mockResponse.start()
    path = reverse("globalDimension")
    response = client.get(path, content_type="application/json")
    mockResponse.stop()
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["values"][0]["dimension"] == "WarehouseCode"
    assert response.json()["data"][0]["published"] == False

    # Checking the data dimensions
    mockResponse.start()
    path = reverse("dimension")
    response = client.get(path, content_type="application/json")
    assert response.json()["data"][0]["dimension"] == "Category"
    assert response.json()["data"][1]["dimension"] == "Region"
    assert response.json()["data"][0]["dataset"] == "demo_dataset"
    assert response.json()["data"][0]["datasetId"] == dataset.id
    assert response.status_code == 200

    # Getting global dimension by Id
    mockResponse.start()
    path = reverse("globalDimension")
    GlobalDimsId = client.get(path, content_type="application/json")
    path = reverse(
        "globalDimensionId", kwargs={"id": GlobalDimsId.json()["data"][0]["id"]}
    )
    response = client.get(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"] == True
    assert response.json()["data"]["id"] == GlobalDimsId.json()["data"][0]["id"]

    # Checking the exception of getGlobalDimensionById
    mockResponse.start()
    path = reverse("globalDimension")
    GlobalDimsId = 1001
    path = reverse("globalDimensionId", kwargs={"id": GlobalDimsId})
    response = client.get(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"] == False
    assert (
        response.json()["message"]
        == "Error occurs while fetching global dimension by Id"
    )

    # Getting the global dimension id for updating
    mockResponse.start()
    path = reverse("globalDimension")
    GlobalDimsId = client.get(path, content_type="application/json")
    GlobalDimsId = GlobalDimsId.json()["data"][0]["id"]
    mockResponse.stop()

    # Updating the exsisting global dimension Id
    mockResponse.start()
    path = reverse("updateGlobalDimension", kwargs={"id": GlobalDimsId})
    payload = {"name": "updatedTest", "dimensionalValues": [], "published": True}
    response = client.post(path, payload, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"] == True
    assert response.status_code == 200
    assert response.json()["message"] == "Global Dimension updated successfully"

    # Getting the updated global dimension
    mockResponse.start()
    path = reverse("globalDimension")
    response = client.get(path, content_type="application/json")
    mockResponse.stop()
    assert response.json()["data"][0]["values"] == []
    assert response.json()["data"][0]["published"] == True

    # Testing the api of non global dimension for indexing
    mockResponse.start()
    result = GlobalDimensionServices.nonGlobalDimensionForIndexing()
    expectedResults = {
        "success": True,
        "data": [
            {
                "dataset": "demo_dataset",
                "datasetId": dataset.id,
                "dimension": "Category",
            },
            {"dataset": "demo_dataset", "datasetId": dataset.id, "dimension": "Region"},
        ],
    }

    assert result == expectedResults
    assert result["data"][0]["dataset"] == "demo_dataset"
    assert result["data"][0]["datasetId"] == dataset.id
