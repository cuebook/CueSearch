import pytest
import unittest
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from anomaly.models import AnomalyDefinition

@pytest.mark.django_db(transaction=True)
def test_runstatus(client, mocker):
    """
    Test cases for anomalyDefinition
    """

    anomalyDef = mixer.blend("anomaly.AnomalyDefinition", periodicTask=None)
    runStatus = mixer.blend("anomaly.RunStatus", anomalyDefinition=anomalyDef, status="RUNNING")

    path = reverse("getDetectionRuns", kwargs={"anomalyDefId": anomalyDef.id})
    response = client.get(path)
    assert response.status_code == 200
    assert response.data["data"]["count"] == 1
    assert response.data["data"]["runStatuses"][0]["status"] == "RUNNING"

    path = reverse("isTaskRunning", kwargs={"anomalyDefId": anomalyDef.id})
    response = client.get(path)
    assert response.status_code == 200
    assert response.data["data"]["isRunning"]

    runStatus.status = "SUCCESS"
    runStatus.save()

    response = client.get(path)
    assert response.status_code == 200
    assert not response.data["data"]["isRunning"]

    path = reverse("runStatusAnomalies", kwargs={"runStatusId": runStatus.id})
    response = client.get(path)
    assert response.status_code == 200
    assert response.data["data"] == []

    anomaly = mixer.blend("anomaly.Anomaly", latestRun=runStatus, anomalyDefinition=anomalyDef, dimensionVal="Lko")

    response = client.get(path)
    assert response.status_code == 200
    assert response.data["data"] == [{"dimensionVal": "Lko", "id": anomaly.id, "published": False}]