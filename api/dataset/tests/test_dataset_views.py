import pytest
import unittest
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer


@pytest.mark.django_db(transaction=True)
def test_datasets(client, mocker):
    # Get dataset when no entry
    path = reverse("datasets")
    response = client.get(path)
    assert response.status_code == 200
    assert not response.data["data"]

    # Create dataset
    connection = mixer.blend("dataset.connection")

    path = reverse("createDataset")
    data = {
        "name": "something",
        "sql": "SELECT * from TEST_TABLE",
        "connectionId": connection.id,
        "metrics": ["Amount", "Quantity"],
        "dimensions": ["Category", "Region"],
        "timestamp": "CreatedAt",
        "granularity": "day",
        "isNonRollup": False,
    }
    response = client.post(path, data=data, content_type="application/json")

    assert response.status_code == 200
    assert response.data["success"]

    # Get datasets
    path = reverse("datasets")
    response = client.get(path)
    assert response.status_code == 200
    assert response.data["data"]
    assert set(response.data["data"][0].keys()) == set(
        ["connection", "granularity", "name", "id", "connectionName"]
    )

    dataset = response.data["data"][0]

    # Get dataset
    path = reverse("dataset", kwargs={"datasetId": dataset["id"]})
    response = client.get(path)

    assert response.status_code == 200
    assert response.data["data"]
    assert response.data["data"]["name"] == "something"
    assert set(response.data["data"].keys()) == set(
        [
            "id",
            "name",
            "sql",
            "connection",
            "dimensions",
            "metrics",
            "granularity",
            "timestampColumn",
        ]
    )

    # Update dataset
    data = {
        "name": "anything",
        "sql": "SELECT * from TEST_TABLE",
        "connectionId": connection.id,
        "metrics": ["Amount", "Quantity"],
        "dimensions": ["Category", "Region"],
        "timestamp": "CreatedAt",
        "granularity": "day",
        "isNonRollup": False,
    }
    path = reverse("dataset", kwargs={"datasetId": dataset["id"]})
    response = client.post(path, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"]

    # Get dataset
    path = reverse("dataset", kwargs={"datasetId": dataset["id"]})
    response = client.get(path)

    assert response.status_code == 200
    assert response.data["data"]
    assert response.data["data"]["name"] == "anything"

    # Delete dataset
    path = reverse("dataset", kwargs={"datasetId": dataset["id"]})
    response = client.delete(path)

    assert response.status_code == 200
    assert response.data["success"]

    # Get datasets
    path = reverse("datasets")
    response = client.get(path)
    assert response.status_code == 200
    assert not response.data["data"]
