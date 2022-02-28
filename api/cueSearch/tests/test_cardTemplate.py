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
    assert response.status_code == 200
    assert response.data["success"]

    # Getting the existing templates
    path = reverse("getTemplates")
    response = client.get(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"]
    response.json()["data"][0]["templateName"] == "Sample"
    response.json()["data"][0]["published"] == False
    id = response.json()["data"][0]["id"]

    # Publishing the existing templates
    payload = {"id": id, "published": False}
    path = reverse("pubCardTemplates")
    response = client.post(path, payload, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"]

    # Getting the template by Id
    path = reverse("getTemplatesById", kwargs={"id": id})
    response = client.get(path, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"]

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
    assert response.status_code == 200
    assert response.data["success"]
    response.json()["data"][0]["templateName"] == "updatedSample"
    response.json()["data"][0]["title"] == "updatedSample"

    # Deleting the existing templates
    path = reverse("cardTemplateDelete", kwargs={"id": id})
    response = client.delete(path, payload, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"]


@pytest.mark.django_db(transaction=True)
def testVerifyCardTemplates(client, mocker):

    templateTitle = '{% load event_tags %} {% for filterDim in filterDimensions %} {% conditionalCount searchResults \'dimension\' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} Comparison of <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{metricName}}</span> among <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{filterDim}}</span> values in <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{dataset}}</span> +-; {% endfor %} {% endif %} {% endfor %}'
    templateText = '{% load event_tags %} {% for filterDim in filterDimensions %} {% conditionalCount searchResults \'dimension\' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} This chart displays filtered values on dimension <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{filterDim}}</span> along with other filters applied i.e. <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{filter|safe}}</span> for metric <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{metricName}}</span> on dataset <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{dataset}}</span> +-; {% endfor %} {% endif %} {% endfor %}'
    templateSql = '{% load event_tags %} {% for filterDim in filterDimensions %} {% conditionalCount searchResults \'dimension\' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} SELECT "templatetable"."{{ timestampColumn }}", "templatetable"."{{ filterDim }}", SUM("templatetable"."{{ metricName }}") as {{metricName}} FROM ({{ datasetSql|safe }}) AS templatetable WHERE {% for orResults in groupedResultsForFilter %} {% for orResult in orResults %} "templatetable"."{{ orResult.dimension }}" = \'{{ orResult.value }}\' OR {% endfor %} True AND {% endfor %} True GROUP BY 1, 2 limit 500 +-; {% endfor %} {% endif %} {% endfor %}'
    noVariableTemplateSql = '{% load event_tags %} {% for filterDim in filterDimensionx %} {% conditionalCount searchResults \'dimension\' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} SELECT "templatetable"."{{ timestampColumn }}", "templatetable"."{{ filterDim }}", SUM("templatetable"."{{ metricName }}") as {{metricName}} FROM ({{ datasetSql|safe }}) AS templatetable WHERE {% for orResults in groupedResultsForFilter %} {% for orResult in orResults %} "templatetable"."{{ orResult.dimension }}" = \'{{ orResult.value }}\' OR {% endfor %} True AND {% endfor %} True GROUP BY 1, 2 limit 500 +-; {% endfor %} {% endif %} {% endfor %}'

    # Testing the card templete api
    path = reverse("verifyCardTemplates")
    payload = {
        "templateTitle": templateTitle,
        "templateText": templateText,
        "templateSql": templateSql,
    }
    response = client.post(path, payload, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"] == True

    path = reverse("verifyCardTemplates")
    payload = {
        "templateTitle": templateTitle,
        "templateText": templateText,
        "templateSql": noVariableTemplateSql,
    }
    response = client.post(path, payload, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"] == False

    # different number of values returning from templateText vs templateSql
    path = reverse("verifyCardTemplates")
    payload = {
        "templateTitle": templateTitle,
        "templateText": "",
        "templateSql": noVariableTemplateSql,
    }
    response = client.post(path, payload, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"] == False

    # empty values for templateText and templateSql resulting to valid template
    path = reverse("verifyCardTemplates")
    payload = {
        "templateTitle": "",
        "templateText": "",
        "templateSql": "",
    }
    response = client.post(path, payload, content_type="application/json")
    assert response.status_code == 200
    assert response.data["success"] == True
