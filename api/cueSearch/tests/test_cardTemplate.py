import pytest
from unittest import mock
from django.urls import reverse
from mixer.backend.django import mixer


@pytest.mark.django_db(transaction=True)
def testCardTemplates(client, mocker):
    # connection Type
    connectionType = mixer.blend(
        "dataset.connectionType", name="TEST_DRUID", id=1, label="test_druid"
    )
    path = reverse("createCardTemplates")
    payload = {
        "templateName": "Sample",
        "title": "Sample",
        "sql": "Sample",
        "bodyText": "Sample",
        "renderType": "table",
        "connectionTypeId": 1,
    }
    response = client.post(path, payload, content_type="application/json")
    assert response.data["success"]
    assert response.status_code == 200

    # Getting the existing templates
    path = reverse("getTemplates")
    response = client.get(path, content_type="application/json")
    assert response.data["success"]
    assert response.status_code == 200
    response.json()["data"][0]["templateName"] == "Sample"
    response.json()["data"][0]["published"] == False
    id = response.json()["data"][0]["id"]

    # Publishing the existing templates
    payload = {"id": id, "published": False}
    path = reverse("pubCardTemplates")
    response = client.post(path, payload, content_type="application/json")
    assert response.data["success"]
    assert response.status_code == 200

    # Getting the template by Id
    path = reverse("getTemplatesById", kwargs={"id": id})
    response = client.get(path, content_type="application/json")
    assert response.data["success"]
    assert response.status_code == 200

    # Updating the card template
    payload = {
        "templateName": "updatedSample",
        "title": "updatedSample",
        "sql": "Sample",
        "bodyText": "Sample",
        "renderType": "table",
        "connectionTypeId": 1,
    }
    path = reverse("updateCardTemplate", kwargs={"id": id})
    response = client.post(path, payload, content_type="application/json")

    # Getting the existing templates
    path = reverse("getTemplates")
    response = client.get(path, content_type="application/json")
    assert response.data["success"]
    assert response.status_code == 200
    response.json()["data"][0]["templateName"] == "updatedSample"
    response.json()["data"][0]["title"] == "updatedSample"

    # Deleting the existing templates
    path = reverse("cardTemplateDelete", kwargs={"id": id})
    response = client.delete(path, payload, content_type="application/json")
    assert response.data["success"]
    assert response.status_code == 200

    

    # Testing the card templete api
    path = reverse("verifyCardTemplates")
    payload = {
      "templateTitle": 'Split on Filter Dimension',
      "templateText" : '<span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{dataset}}</span>',
      "templateSql": "SELECT * FROM ({{ datasetSql|safe }}) WHERE {{filter|safe}} limit 500",
    }
    response = client.post(path, payload, content_type="application/json")
    assert response.data["success"] == True
    assert response.status_code == 200
    assert response.json()['message'] == 'Template rendered successfully'



    path = reverse("verifyCardTemplates")
    payload = {
      "templateTitle": 'Metric Chart',
      "templateText" : '<span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{dataset}}</span>',
      "templateSql":"{% load event_tags %} {% for filterDim in filterDimensions %} {% conditionalCount searchResults 'dimension' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} SELECT ({{ timestampColumn }}), {{ filterDim }}, SUM({{ metricName }}) as {{metricName}} FROM ({{ datasetSql|safe }}) WHERE {{filter|safe}} GROUP BY 1, 2 limit 500 +-; {% endfor %} {% endif %} {% endfor %}",
    }
    response = client.post(path, payload, content_type="application/json")
    assert response.data["success"] == False
    assert response.status_code == 200
    assert response.json()['message'] == 'Error occur during rendering'
