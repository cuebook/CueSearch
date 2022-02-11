import pytest
from cueSearch.services.utils import makeFilter, addDimensionsInParam, getChartMetaData


@pytest.mark.django_db(transaction=True)
def testMakeFilter():
    payload = [
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
            "value": "ASOS",
            "dimension": "Brand",
            "globalDimensionName": "Brand",
            "user_entity_identifier": "Brand",
            "id": 11,
            "dataset": "order",
            "datasetId": 1,
            "type": "GLOBALDIMENSION",
        },
    ]
    filter = makeFilter(payload)
    assert filter == "( ( Brand = 'ASOS' ) ) AND ( State = 'AL' OR State = 'AK' )"

    dimensionPayload = [
        {
            "value": "AL",
            "dimension": "State",
            "globalDimensionName": "State",
            "user_entity_identifier": "State",
            "id": 12,
            "dataset": "HourlyOrders",
            "datasetId": 3,
            "type": "GLOBALDIMENSION",
        },
        {
            "value": "AK",
            "dimension": "State",
            "globalDimensionName": "State",
            "user_entity_identifier": "State",
            "id": 12,
            "dataset": "HourlyOrders",
            "datasetId": 3,
            "type": "GLOBALDIMENSION",
        },
        {
            "value": "ASOS",
            "dimension": "Brand",
            "globalDimensionName": "Brand",
            "user_entity_identifier": "Brand",
            "id": 11,
            "dataset": "HourlyOrders",
            "datasetId": 3,
            "type": "GLOBALDIMENSION",
        },
    ]

    listOfDimension = addDimensionsInParam(dimensionPayload)
    assert listOfDimension == ["Brand", "State"]

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
        "sql": "  SELECT (OrderDate), Brand, SUM(OrderAmount) as OrderAmount FROM (\nSELECT DATE_TRUNC('DAY', __time) as OrderDate,\nBrand, Color, State,\nSUM(\"count\") as Orders, ROUND(sum(OrderAmount),2) as OrderAmount, sum(OrderQuantity) as OrderQuantity\nFROM FAKEORDERS\nWHERE __time >= CURRENT_TIMESTAMP - INTERVAL '13' MONTH \nGROUP BY 1, 2, 3, 4\nORDER BY 1) WHERE ( ( Brand = 'Adidas' ) ) AND ( State = 'AL' OR State = 'AK' ) GROUP BY 1, 2 limit 500 ",
    }
    data = [
        {
            "OrderDate": "2021-01-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 77780.0,
        },
        {
            "OrderDate": "2021-01-12T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 11490.0,
        },
        {
            "OrderDate": "2021-01-13T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-01-16T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 11160.0,
        },
        {
            "OrderDate": "2021-01-17T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6290.0,
        },
        {
            "OrderDate": "2021-12-05T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5310.0,
        },
        {
            "OrderDate": "2021-12-10T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4700.0,
        },
        {
            "OrderDate": "2021-12-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6155.0,
        },
        {
            "OrderDate": "2021-12-12T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3525.0,
        },
        {
            "OrderDate": "2021-12-15T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 46400.0,
        },
        {
            "OrderDate": "2021-12-16T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 14005.0,
        },
        {
            "OrderDate": "2021-12-18T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6415.0,
        },
        {
            "OrderDate": "2021-12-19T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3960.0,
        },
        {
            "OrderDate": "2021-12-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 10660.0,
        },
        {
            "OrderDate": "2021-12-21T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6120.0,
        },
        {
            "OrderDate": "2021-12-22T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9715.0,
        },
        {
            "OrderDate": "2021-12-23T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 26087.5,
        },
        {
            "OrderDate": "2021-12-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 40852.5,
        },
        {
            "OrderDate": "2021-12-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 37812.5,
        },
        {
            "OrderDate": "2021-12-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2500.0,
        },
        {
            "OrderDate": "2021-12-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9320.0,
        },
        {
            "OrderDate": "2021-12-30T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1755.0,
        },
        {
            "OrderDate": "2022-01-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2450.0,
        },
    ]

    chartMetaData = getChartMetaData(params, data)
    assert chartMetaData == {
        "xColumn": "OrderDate",
        "yColumn": "OrderAmount",
        "scale": {
            "OrderDate": {"type": "time", "mask": "M/D"},
            "Brand": {"alias": "Brand"},
        },
        "order": "O",
        "color": "Brand",
    }
