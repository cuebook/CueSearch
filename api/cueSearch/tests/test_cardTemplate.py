import pytest
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


    # Verify the card templete by giving the wrong value
    path = reverse("verifyCardTemplates")
    payload = {
        "sql": "Sample",
    }
    response = client.post(path, payload, content_type="application/json")
    assert response.data["success"] == False
    assert response.status_code == 200
    assert response.json()['message'] == 'Error in rendering templates'

