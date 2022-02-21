from builtins import breakpoint
from logging import exception
import pytest
from unittest import mock
from django.urls import reverse
from mixer.backend.django import mixer
from utils.apiResponse import ApiResponse
from dataset.models import Dataset


@pytest.mark.django_db(transaction=True)
def test_getSearchCard(client, mocker):
    """
    Test case for delete global dimension
    """
    connection = mixer.blend("dataset.connection")

    testDataset = mixer.blend(
        "dataset.dataset",
        name="orders",
        id=1,
        dimensions='["Brand", "Color", "State"]',
        metrics='["Orders", "OrderAmount", "OrderQuantity"]',
        granularity="day",
        timestampColumn="TestDate",
        sql="Select * from testTable",
    )
    searchCardTemplateForTable = mixer.blend(
        "cueSearch.searchCardTemplate",
        templateName="Test table data",
        title="Test SQL Card ",
        bodyText='This table displays raw data for dataset <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{dataset}}</span> with filter <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{filter}}</span> ',
        supportedVariables="granularity, datasetName, dimension, value",
        sql="SELECT * FROM ({{ datasetSql|safe }}) WHERE {{filter|safe}} limit 500",
        renderType="table",
    )
    searchCardTemplateForChart = mixer.blend(
        "cueSearch.searchCardTemplate",
        templateName="Split on Filter Dimension Test chart",
        title="Test Chart Card ",
        bodyText='{% load event_tags %} {% for filterDim in filterDimensions %} {% conditionalCount searchResults \'dimension\' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} This chart displays filtered values on dimension <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{filterDim}}</span> along with other filters applied i.e. <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{filter|safe}}</span> for metric <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{metricName}}</span> on dataset <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{dataset}}</span> +-; {% endfor %} {% endif %} {% endfor %}',
        supportedVariables="granularity, datasetName, dimension, value",
        sql="{% load event_tags %} {% for filterDim in filterDimensions %} {% conditionalCount searchResults 'dimension' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} SELECT ({{ timestampColumn }}), {{ filterDim }}, SUM({{ metricName }}) as {{metricName}} FROM ({{ datasetSql|safe }}) WHERE {{filter|safe}} GROUP BY 1, 2 limit 500 +-; {% endfor %} {% endif %} {% endfor %}",
        renderType="line",
    )

    # create demo data for global dimension
    mockResponse = mocker.patch(
        "cueSearch.elasticSearch.elastic_search_indexing.ESIndexingUtils.runAllIndexDimension",
        new=mock.MagicMock(autospec=True, return_value=True),
    )
    mockResponse.start()
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
    mockResponse.start()
    response = client.get(path)
    mockResponse.stop()
    assert response.data["data"][0]["values"][0]["datasetId"] == dataset.id
    assert response.data["success"]
    assert response.status_code == 200
    gd_id = response.data["data"][0]["id"]

    # Get Search Card
    path = reverse("getSearchCards")
    mockResponse.start()
    payload = [
        {
            "value": "AD_Data",
            "user_entity_identifier": "Data",
            "id": 8,
            "type": "Data",
            "label": "AD",
            "searchType": "GLOBALDIMENSION",
        }
    ]
    response = client.post(path, payload, content_type="application/json")
    mockResponse.stop()
    assert response.data["success"]
    assert response.status_code == 200
    assert response.json()['data'][0]['params']['datasetId'] == dataset.id
    assert response.json()['data'][0]['params']['searchResults'][0]['value'] == 'AD'


    # Get Search Card(Detailed test case)
    searchResult = [
        {
            "value": "Adidas",
            "dimension": "Brand",
            "globalDimensionName": "Brand",
            "user_entity_identifier": "Brand",
            "id": 11,
            "dataset": "order",
            "datasetId": 1,
            "type": "GLOBALDIMENSION",
        }
    ]
    searchPayload = [
        {
            "value": "Adidas_Brand",
            "user_entity_identifier": "Brand",
            "id": 11,
            "type": "Brand",
            "label": "Adidas",
            "searchType": "GLOBALDIMENSION",
        }
    ]
    mockResponse = mocker.patch(
        "cueSearch.services.searchCardTemplate.SearchCardTemplateServices.ElasticSearchQueryResultsForOnSearchQuery",
        new=mock.MagicMock(autospec=True, return_value=searchResult),
    )
    mockResponse.start()
    path = reverse("getSearchCards")
    response = client.post(path, searchPayload, content_type="application/json")
    assert response
    assert response.json()["data"][0]["params"]["filter"] == "( Brand = 'Adidas' )"
    assert (
        response.json()["data"][0]["params"]["sql"]
        == "SELECT * FROM (Select * from testTable) WHERE ( Brand = 'Adidas' ) limit 500"
    )

    mockResponse.stop()
    # Get Search Card Data
    params = {
        "datasetId": 1,
        "searchResults": [
            {
                "value": "AL",
                "dimension": "State",
                "globalDimensionName": "State",
                "user_entity_identifier": "State",
                "id": 12,
                "dataset": "order",
                "datasetId": 1,
                "type": "GLOBALDIMENSION",
            },
            {
                "value": "AK",
                "dimension": "State",
                "globalDimensionName": "State",
                "user_entity_identifier": "State",
                "id": 12,
                "dataset": "order",
                "datasetId": 1,
                "type": "GLOBALDIMENSION",
            },
            {
                "value": "Adidas",
                "dimension": "Brand",
                "globalDimensionName": "Brand",
                "user_entity_identifier": "Brand",
                "id": 11,
                "dataset": "order",
                "datasetId": 1,
                "type": "GLOBALDIMENSION",
            },
        ],
        "filter": "( ( Brand = 'Adidas' ) ) AND ( State = 'AL' OR State = 'AK' )",
        "filterDimensions": ["Brand", "State"],
        "templateSql": "{% load event_tags %} {% for filterDim in filterDimensions %} {% conditionalCount searchResults 'dimension' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} SELECT ({{ timestampColumn }}), {{ filterDim }}, SUM({{ metricName }}) as {{metricName}} FROM ({{ datasetSql|safe }}) WHERE {{filter|safe}} GROUP BY 1, 2 limit 500 +-; {% endfor %} {% endif %} {% endfor %}",
        "templateTitle": '{% load event_tags %} {% for filterDim in filterDimensions %} {% conditionalCount searchResults \'dimension\' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} Comparison of <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{metricName}}</span> among <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{filterDim}}</span> values in <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{dataset}}</span> +-; {% endfor %} {% endif %} {% endfor %}',
        "templateText": '{% load event_tags %} {% for filterDim in filterDimensions %} {% conditionalCount searchResults \'dimension\' filterDim as dimCount %} {% if dimCount > 1 %} {% for metricName in metrics %} This chart displays filtered values on dimension <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{filterDim}}</span> along with other filters applied i.e. <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{filter|safe}}</span> for metric <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{metricName}}</span> on dataset <span style="background:#eee; padding: 0 4px; border-radius: 4px;">{{dataset}}</span> +-; {% endfor %} {% endif %} {% endfor %}',
        "renderType": "line",
        "dataset": "order",
        "dimensions": ["Brand", "Color", "State"],
        "metrics": ["Orders", "OrderAmount", "OrderQuantity"],
        "timestampColumn": "OrderDate",
        "datasetSql": "\nSELECT DATE_TRUNC('DAY', __time) as OrderDate,\nBrand, Color, State,\nSUM(\"count\") as Orders, ROUND(sum(OrderAmount),2) as OrderAmount, sum(OrderQuantity) as OrderQuantity\nFROM FAKEORDERS\nWHERE __time >= CURRENT_TIMESTAMP - INTERVAL '13' MONTH \nGROUP BY 1, 2, 3, 4\nORDER BY 1",
        "granularity": "day",
        "sql": "  SELECT (OrderDate), State, SUM(OrderQuantity) as OrderQuantity FROM (\nSELECT DATE_TRUNC('DAY', __time) as OrderDate,\nBrand, Color, State,\nSUM(\"count\") as Orders, ROUND(sum(OrderAmount),2) as OrderAmount, sum(OrderQuantity) as OrderQuantity\nFROM FAKEORDERS\nWHERE __time >= CURRENT_TIMESTAMP - INTERVAL '13' MONTH \nGROUP BY 1, 2, 3, 4\nORDER BY 1) WHERE ( ( Brand = 'Adidas' ) ) AND ( State = 'AL' OR State = 'AK' ) GROUP BY 1, 2 limit 500 ",
    }

    data = [
        {"OrderDate": "2021-01-11T00:00:00.000Z", "State": "AK", "Orders": 25},
        {"OrderDate": "2021-01-11T00:00:00.000Z", "State": "AL", "Orders": 14},
        {"OrderDate": "2021-01-12T00:00:00.000Z", "State": "AK", "Orders": 5},
        {"OrderDate": "2021-01-13T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-16T00:00:00.000Z", "State": "AK", "Orders": 6},
        {"OrderDate": "2021-01-16T00:00:00.000Z", "State": "AL", "Orders": 7},
        {"OrderDate": "2021-01-17T00:00:00.000Z", "State": "AK", "Orders": 4},
        {"OrderDate": "2021-01-19T00:00:00.000Z", "State": "AK", "Orders": 15},
        {"OrderDate": "2021-01-20T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-01-22T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-23T00:00:00.000Z", "State": "AL", "Orders": 2},
        {"OrderDate": "2021-01-24T00:00:00.000Z", "State": "AK", "Orders": 6},
        {"OrderDate": "2021-01-25T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-26T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-01-26T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-01-27T00:00:00.000Z", "State": "AK", "Orders": 4},
        {"OrderDate": "2021-01-27T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-01-28T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-28T00:00:00.000Z", "State": "AL", "Orders": 2},
        {"OrderDate": "2021-01-29T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-31T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-31T00:00:00.000Z", "State": "AL", "Orders": 1},
        {"OrderDate": "2021-02-01T00:00:00.000Z", "State": "AK", "Orders": 11},
        {"OrderDate": "2021-02-01T00:00:00.000Z", "State": "AL", "Orders": 8},
        {"OrderDate": "2021-02-02T00:00:00.000Z", "State": "AK", "Orders": 17},
        {"OrderDate": "2021-02-02T00:00:00.000Z", "State": "AL", "Orders": 32},
        {"OrderDate": "2021-02-03T00:00:00.000Z", "State": "AL", "Orders": 8},
        {"OrderDate": "2021-02-04T00:00:00.000Z", "State": "AL", "Orders": 5},
        {"OrderDate": "2021-02-05T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-02-05T00:00:00.000Z", "State": "AL", "Orders": 5},
        {"OrderDate": "2021-02-06T00:00:00.000Z", "State": "AL", "Orders": 1},
        {"OrderDate": "2021-02-07T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-02-07T00:00:00.000Z", "State": "AL", "Orders": 10},
        {"OrderDate": "2021-02-08T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-02-09T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-02-10T00:00:00.000Z", "State": "AL", "Orders": 5},
        {"OrderDate": "2021-02-11T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-02-11T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-02-13T00:00:00.000Z", "State": "AK", "Orders": 2},
        {"OrderDate": "2021-02-14T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-02-14T00:00:00.000Z", "State": "AL", "Orders": 4},
        {"OrderDate": "2021-02-17T00:00:00.000Z", "State": "AK", "Orders": 2},
        {"OrderDate": "2021-02-20T00:00:00.000Z", "State": "AL", "Orders": 1},
        {"OrderDate": "2021-02-22T00:00:00.000Z", "State": "AK", "Orders": 2},
        {"OrderDate": "2021-02-23T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-02-24T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-02-26T00:00:00.000Z", "State": "AK", "Orders": 1},
    ]
    res = ApiResponse("Error in fetching data")
    res.update(True, "Successfully retrieved dataset", data)

    mockResponse = mocker.patch(
        "dataset.services.Datasets.getDatasetData",
        new=mock.MagicMock(autospec=True, return_value=res),
    )
    path = reverse("getSearchCardData")
    response = client.post(path, params, content_type="application/json")

    responseData = [
        {"OrderDate": "2021-01-11T00:00:00.000Z", "State": "AK", "Orders": 25},
        {"OrderDate": "2021-01-11T00:00:00.000Z", "State": "AL", "Orders": 14},
        {"OrderDate": "2021-01-12T00:00:00.000Z", "State": "AK", "Orders": 5},
        {"OrderDate": "2021-01-13T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-16T00:00:00.000Z", "State": "AK", "Orders": 6},
        {"OrderDate": "2021-01-16T00:00:00.000Z", "State": "AL", "Orders": 7},
        {"OrderDate": "2021-01-17T00:00:00.000Z", "State": "AK", "Orders": 4},
        {"OrderDate": "2021-01-19T00:00:00.000Z", "State": "AK", "Orders": 15},
        {"OrderDate": "2021-01-20T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-01-22T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-23T00:00:00.000Z", "State": "AL", "Orders": 2},
        {"OrderDate": "2021-01-24T00:00:00.000Z", "State": "AK", "Orders": 6},
        {"OrderDate": "2021-01-25T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-26T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-01-26T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-01-27T00:00:00.000Z", "State": "AK", "Orders": 4},
        {"OrderDate": "2021-01-27T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-01-28T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-28T00:00:00.000Z", "State": "AL", "Orders": 2},
        {"OrderDate": "2021-01-29T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-31T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-01-31T00:00:00.000Z", "State": "AL", "Orders": 1},
        {"OrderDate": "2021-02-01T00:00:00.000Z", "State": "AK", "Orders": 11},
        {"OrderDate": "2021-02-01T00:00:00.000Z", "State": "AL", "Orders": 8},
        {"OrderDate": "2021-02-02T00:00:00.000Z", "State": "AK", "Orders": 17},
        {"OrderDate": "2021-02-02T00:00:00.000Z", "State": "AL", "Orders": 32},
        {"OrderDate": "2021-02-03T00:00:00.000Z", "State": "AL", "Orders": 8},
        {"OrderDate": "2021-02-04T00:00:00.000Z", "State": "AL", "Orders": 5},
        {"OrderDate": "2021-02-05T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-02-05T00:00:00.000Z", "State": "AL", "Orders": 5},
        {"OrderDate": "2021-02-06T00:00:00.000Z", "State": "AL", "Orders": 1},
        {"OrderDate": "2021-02-07T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-02-07T00:00:00.000Z", "State": "AL", "Orders": 10},
        {"OrderDate": "2021-02-08T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-02-09T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-02-10T00:00:00.000Z", "State": "AL", "Orders": 5},
        {"OrderDate": "2021-02-11T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-02-11T00:00:00.000Z", "State": "AL", "Orders": 3},
        {"OrderDate": "2021-02-13T00:00:00.000Z", "State": "AK", "Orders": 2},
        {"OrderDate": "2021-02-14T00:00:00.000Z", "State": "AK", "Orders": 3},
        {"OrderDate": "2021-02-14T00:00:00.000Z", "State": "AL", "Orders": 4},
        {"OrderDate": "2021-02-17T00:00:00.000Z", "State": "AK", "Orders": 2},
        {"OrderDate": "2021-02-20T00:00:00.000Z", "State": "AL", "Orders": 1},
        {"OrderDate": "2021-02-22T00:00:00.000Z", "State": "AK", "Orders": 2},
        {"OrderDate": "2021-02-23T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-02-24T00:00:00.000Z", "State": "AK", "Orders": 1},
        {"OrderDate": "2021-02-26T00:00:00.000Z", "State": "AK", "Orders": 1},
    ]

    assert response.json()["success"] == True
    assert response.json()["data"]["chartMetaData"] == {
        "xColumn": "OrderDate",
        "yColumn": "Orders",
        "scale": {
            "OrderDate": {"type": "time", "mask": "M/D"},
            "State": {"alias": "State"},
        },
        "order": "O",
        "color": "State",
    }
    assert response.json()["data"]["data"] == responseData
