from audioop import add
from builtins import breakpoint
from http import client
from logging import exception
import re

from django.db import utils
import pytest
from unittest import mock
from django.urls import reverse
import unittest
from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient
from mixer.backend.django import mixer
from dataset.models import Dataset
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
            "OrderDate": "2021-01-19T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 19400.0,
        },
        {
            "OrderDate": "2021-01-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7120.0,
        },
        {
            "OrderDate": "2021-01-22T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-01-23T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1890.0,
        },
        {
            "OrderDate": "2021-01-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 13750.0,
        },
        {
            "OrderDate": "2021-01-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2900.0,
        },
        {
            "OrderDate": "2021-01-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 17320.0,
        },
        {
            "OrderDate": "2021-01-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 13550.0,
        },
        {
            "OrderDate": "2021-01-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7580.0,
        },
        {
            "OrderDate": "2021-01-29T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2900.0,
        },
        {
            "OrderDate": "2021-01-31T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4430.0,
        },
        {
            "OrderDate": "2021-02-01T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 37847.5,
        },
        {
            "OrderDate": "2021-02-02T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 105565.0,
        },
        {
            "OrderDate": "2021-02-03T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 13775.0,
        },
        {
            "OrderDate": "2021-02-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 8570.0,
        },
        {
            "OrderDate": "2021-02-05T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 11925.0,
        },
        {
            "OrderDate": "2021-02-06T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-02-07T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 25795.0,
        },
        {
            "OrderDate": "2021-02-08T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4500.0,
        },
        {
            "OrderDate": "2021-02-09T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9700.0,
        },
        {
            "OrderDate": "2021-02-10T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5895.0,
        },
        {
            "OrderDate": "2021-02-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 8190.0,
        },
        {
            "OrderDate": "2021-02-13T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2100.0,
        },
        {
            "OrderDate": "2021-02-14T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 18330.0,
        },
        {
            "OrderDate": "2021-02-17T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5580.0,
        },
        {
            "OrderDate": "2021-02-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1530.0,
        },
        {
            "OrderDate": "2021-02-22T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4680.0,
        },
        {
            "OrderDate": "2021-02-23T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 945.0,
        },
        {
            "OrderDate": "2021-02-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5220.0,
        },
        {
            "OrderDate": "2021-02-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3430.0,
        },
        {
            "OrderDate": "2021-02-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2880.0,
        },
        {
            "OrderDate": "2021-03-02T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 12940.0,
        },
        {
            "OrderDate": "2021-03-03T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 77760.0,
        },
        {
            "OrderDate": "2021-03-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9060.0,
        },
        {
            "OrderDate": "2021-03-06T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4970.0,
        },
        {
            "OrderDate": "2021-03-07T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1890.0,
        },
        {
            "OrderDate": "2021-03-08T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7470.0,
        },
        {
            "OrderDate": "2021-03-10T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5040.0,
        },
        {
            "OrderDate": "2021-03-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3060.0,
        },
        {
            "OrderDate": "2021-03-12T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6120.0,
        },
        {
            "OrderDate": "2021-03-13T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3060.0,
        },
        {
            "OrderDate": "2021-03-14T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1530.0,
        },
        {
            "OrderDate": "2021-03-16T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-03-18T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-03-19T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5355.0,
        },
        {
            "OrderDate": "2021-03-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 10990.0,
        },
        {
            "OrderDate": "2021-03-21T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1710.0,
        },
        {
            "OrderDate": "2021-03-22T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5940.0,
        },
        {
            "OrderDate": "2021-03-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 945.0,
        },
        {
            "OrderDate": "2021-03-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3950.0,
        },
        {
            "OrderDate": "2021-03-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3200.0,
        },
        {
            "OrderDate": "2021-03-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9100.0,
        },
        {
            "OrderDate": "2021-03-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3950.0,
        },
        {
            "OrderDate": "2021-03-31T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-04-01T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1530.0,
        },
        {
            "OrderDate": "2021-04-02T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2115.0,
        },
        {
            "OrderDate": "2021-04-05T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 79732.5,
        },
        {
            "OrderDate": "2021-04-08T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1710.0,
        },
        {
            "OrderDate": "2021-04-09T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3660.0,
        },
        {
            "OrderDate": "2021-04-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3770.0,
        },
        {
            "OrderDate": "2021-04-15T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1530.0,
        },
        {
            "OrderDate": "2021-04-16T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 14500.0,
        },
        {
            "OrderDate": "2021-04-17T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 945.0,
        },
        {
            "OrderDate": "2021-04-18T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1530.0,
        },
        {
            "OrderDate": "2021-04-19T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2900.0,
        },
        {
            "OrderDate": "2021-04-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-04-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2790.0,
        },
        {
            "OrderDate": "2021-04-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 22960.0,
        },
        {
            "OrderDate": "2021-04-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 8400.0,
        },
        {
            "OrderDate": "2021-04-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4657.5,
        },
        {
            "OrderDate": "2021-04-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6300.0,
        },
        {
            "OrderDate": "2021-04-29T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 23735.0,
        },
        {
            "OrderDate": "2021-04-30T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 11850.0,
        },
        {
            "OrderDate": "2021-05-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 10750.0,
        },
        {
            "OrderDate": "2021-05-05T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 18665.0,
        },
        {
            "OrderDate": "2021-05-06T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7700.0,
        },
        {
            "OrderDate": "2021-05-07T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9925.0,
        },
        {
            "OrderDate": "2021-05-09T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2070.0,
        },
        {
            "OrderDate": "2021-05-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9720.0,
        },
        {
            "OrderDate": "2021-05-12T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2900.0,
        },
        {
            "OrderDate": "2021-05-14T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 10350.0,
        },
        {
            "OrderDate": "2021-05-15T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1485.0,
        },
        {
            "OrderDate": "2021-05-18T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1700.0,
        },
        {
            "OrderDate": "2021-05-19T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2790.0,
        },
        {
            "OrderDate": "2021-05-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-05-21T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5805.0,
        },
        {
            "OrderDate": "2021-05-22T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7155.0,
        },
        {
            "OrderDate": "2021-05-23T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2850.0,
        },
        {
            "OrderDate": "2021-05-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1425.0,
        },
        {
            "OrderDate": "2021-05-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4920.0,
        },
        {
            "OrderDate": "2021-05-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1160.0,
        },
        {
            "OrderDate": "2021-05-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1840.0,
        },
        {
            "OrderDate": "2021-05-29T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 10260.0,
        },
        {
            "OrderDate": "2021-05-30T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5950.0,
        },
        {
            "OrderDate": "2021-05-31T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7300.0,
        },
        {
            "OrderDate": "2021-06-02T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 23355.0,
        },
        {
            "OrderDate": "2021-06-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-06-06T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 28045.0,
        },
        {
            "OrderDate": "2021-06-09T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9380.0,
        },
        {
            "OrderDate": "2021-06-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2900.0,
        },
        {
            "OrderDate": "2021-06-12T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4650.0,
        },
        {
            "OrderDate": "2021-06-13T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-06-15T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7290.0,
        },
        {
            "OrderDate": "2021-06-16T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1900.0,
        },
        {
            "OrderDate": "2021-06-17T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5455.0,
        },
        {
            "OrderDate": "2021-06-19T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5140.0,
        },
        {
            "OrderDate": "2021-06-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1900.0,
        },
        {
            "OrderDate": "2021-06-21T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5634.0,
        },
        {
            "OrderDate": "2021-06-22T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2320.0,
        },
        {
            "OrderDate": "2021-06-23T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3480.0,
        },
        {
            "OrderDate": "2021-06-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1710.0,
        },
        {
            "OrderDate": "2021-06-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3410.0,
        },
        {
            "OrderDate": "2021-06-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7560.0,
        },
        {
            "OrderDate": "2021-06-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 16685.0,
        },
        {
            "OrderDate": "2021-06-29T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7670.0,
        },
        {
            "OrderDate": "2021-07-02T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-07-03T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1710.0,
        },
        {
            "OrderDate": "2021-07-06T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5375.0,
        },
        {
            "OrderDate": "2021-07-07T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1520.0,
        },
        {
            "OrderDate": "2021-07-09T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 16640.0,
        },
        {
            "OrderDate": "2021-07-12T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 50950.0,
        },
        {
            "OrderDate": "2021-07-13T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 36660.0,
        },
        {
            "OrderDate": "2021-07-14T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 16500.0,
        },
        {
            "OrderDate": "2021-07-15T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9000.0,
        },
        {
            "OrderDate": "2021-07-16T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 27500.0,
        },
        {
            "OrderDate": "2021-07-19T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1445.0,
        },
        {
            "OrderDate": "2021-07-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1387.61,
        },
        {
            "OrderDate": "2021-07-21T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1710.0,
        },
        {
            "OrderDate": "2021-07-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5530.0,
        },
        {
            "OrderDate": "2021-07-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6300.0,
        },
        {
            "OrderDate": "2021-07-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 13845.0,
        },
        {
            "OrderDate": "2021-07-29T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 11275.0,
        },
        {
            "OrderDate": "2021-07-30T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7775.0,
        },
        {
            "OrderDate": "2021-07-31T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1710.0,
        },
        {
            "OrderDate": "2021-08-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2900.0,
        },
        {
            "OrderDate": "2021-08-05T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1305.0,
        },
        {
            "OrderDate": "2021-08-07T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 8200.0,
        },
        {
            "OrderDate": "2021-08-08T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 45602.5,
        },
        {
            "OrderDate": "2021-08-09T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4510.0,
        },
        {
            "OrderDate": "2021-08-10T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1710.0,
        },
        {
            "OrderDate": "2021-08-15T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-08-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 15000.0,
        },
        {
            "OrderDate": "2021-08-21T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 22510.0,
        },
        {
            "OrderDate": "2021-08-22T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3200.0,
        },
        {
            "OrderDate": "2021-08-23T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 11200.0,
        },
        {
            "OrderDate": "2021-08-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5100.0,
        },
        {
            "OrderDate": "2021-08-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1530.0,
        },
        {
            "OrderDate": "2021-09-02T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3700.0,
        },
        {
            "OrderDate": "2021-09-03T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2900.0,
        },
        {
            "OrderDate": "2021-09-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6100.0,
        },
        {
            "OrderDate": "2021-09-05T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6545.0,
        },
        {
            "OrderDate": "2021-09-10T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2610.0,
        },
        {
            "OrderDate": "2021-09-13T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 19440.0,
        },
        {
            "OrderDate": "2021-09-15T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1530.0,
        },
        {
            "OrderDate": "2021-09-16T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 12430.0,
        },
        {
            "OrderDate": "2021-09-18T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3200.0,
        },
        {
            "OrderDate": "2021-09-19T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3015.0,
        },
        {
            "OrderDate": "2021-09-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3230.0,
        },
        {
            "OrderDate": "2021-09-21T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3400.0,
        },
        {
            "OrderDate": "2021-09-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7490.0,
        },
        {
            "OrderDate": "2021-09-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3230.0,
        },
        {
            "OrderDate": "2021-09-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1700.0,
        },
        {
            "OrderDate": "2021-09-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9500.0,
        },
        {
            "OrderDate": "2021-09-29T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5100.0,
        },
        {
            "OrderDate": "2021-09-30T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3910.0,
        },
        {
            "OrderDate": "2021-10-01T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 20212.5,
        },
        {
            "OrderDate": "2021-10-03T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3325.0,
        },
        {
            "OrderDate": "2021-10-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1700.0,
        },
        {
            "OrderDate": "2021-10-06T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5220.0,
        },
        {
            "OrderDate": "2021-10-07T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1312.5,
        },
        {
            "OrderDate": "2021-10-08T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4380.0,
        },
        {
            "OrderDate": "2021-10-10T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1755.0,
        },
        {
            "OrderDate": "2021-10-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7625.0,
        },
        {
            "OrderDate": "2021-10-12T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 13070.0,
        },
        {
            "OrderDate": "2021-10-15T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5605.0,
        },
        {
            "OrderDate": "2021-10-16T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5150.0,
        },
        {
            "OrderDate": "2021-10-17T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1575.0,
        },
        {
            "OrderDate": "2021-10-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 10895.0,
        },
        {
            "OrderDate": "2021-10-22T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 12422.5,
        },
        {
            "OrderDate": "2021-10-23T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 10105.0,
        },
        {
            "OrderDate": "2021-10-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6655.0,
        },
        {
            "OrderDate": "2021-10-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2950.0,
        },
        {
            "OrderDate": "2021-10-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1755.0,
        },
        {
            "OrderDate": "2021-10-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3600.0,
        },
        {
            "OrderDate": "2021-10-29T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1575.0,
        },
        {
            "OrderDate": "2021-10-30T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5605.0,
        },
        {
            "OrderDate": "2021-10-31T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2900.0,
        },
        {
            "OrderDate": "2021-11-01T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9720.0,
        },
        {
            "OrderDate": "2021-11-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1575.0,
        },
        {
            "OrderDate": "2021-11-05T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3330.0,
        },
        {
            "OrderDate": "2021-11-06T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7402.5,
        },
        {
            "OrderDate": "2021-11-07T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 7030.0,
        },
        {
            "OrderDate": "2021-11-08T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5130.0,
        },
        {
            "OrderDate": "2021-11-09T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3755.0,
        },
        {
            "OrderDate": "2021-11-10T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 12109.5,
        },
        {
            "OrderDate": "2021-11-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 171551.0,
        },
        {
            "OrderDate": "2021-11-12T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3950.0,
        },
        {
            "OrderDate": "2021-11-19T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4905.0,
        },
        {
            "OrderDate": "2021-11-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2655.0,
        },
        {
            "OrderDate": "2021-11-21T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2950.0,
        },
        {
            "OrderDate": "2021-11-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 12294.199999999999,
        },
        {
            "OrderDate": "2021-11-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 13738.68,
        },
        {
            "OrderDate": "2021-11-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 8005.0,
        },
        {
            "OrderDate": "2021-11-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 18357.5,
        },
        {
            "OrderDate": "2021-11-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 24755.0,
        },
        {
            "OrderDate": "2021-11-29T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 8025.0,
        },
        {
            "OrderDate": "2021-12-01T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 9620.0,
        },
        {
            "OrderDate": "2021-12-03T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3105.0,
        },
        {
            "OrderDate": "2021-12-04T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5605.0,
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
        {
            "OrderDate": "2022-01-05T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6225.0,
        },
        {
            "OrderDate": "2022-01-06T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2115.0,
        },
        {
            "OrderDate": "2022-01-07T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2950.0,
        },
        {
            "OrderDate": "2022-01-09T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4155.0,
        },
        {
            "OrderDate": "2022-01-10T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2655.0,
        },
        {
            "OrderDate": "2022-01-11T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 45900.0,
        },
        {
            "OrderDate": "2022-01-13T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2950.0,
        },
        {
            "OrderDate": "2022-01-14T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 31920.0,
        },
        {
            "OrderDate": "2022-01-15T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 31910.0,
        },
        {
            "OrderDate": "2022-01-16T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 17240.0,
        },
        {
            "OrderDate": "2022-01-17T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 5555.0,
        },
        {
            "OrderDate": "2022-01-18T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 22905.0,
        },
        {
            "OrderDate": "2022-01-20T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3330.0,
        },
        {
            "OrderDate": "2022-01-21T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 4830.0,
        },
        {
            "OrderDate": "2022-01-23T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2655.0,
        },
        {
            "OrderDate": "2022-01-24T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 8370.0,
        },
        {
            "OrderDate": "2022-01-25T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 10915.0,
        },
        {
            "OrderDate": "2022-01-26T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 6150.0,
        },
        {
            "OrderDate": "2022-01-27T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2655.0,
        },
        {
            "OrderDate": "2022-01-28T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 11880.0,
        },
        {
            "OrderDate": "2022-01-29T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 8215.0,
        },
        {
            "OrderDate": "2022-01-31T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1575.0,
        },
        {
            "OrderDate": "2022-02-01T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 16215.0,
        },
        {
            "OrderDate": "2022-02-02T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 29405.0,
        },
        {
            "OrderDate": "2022-02-03T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 2655.0,
        },
        {
            "OrderDate": "2022-02-05T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1575.0,
        },
        {
            "OrderDate": "2022-02-06T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 11085.0,
        },
        {
            "OrderDate": "2022-02-07T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 3022.5,
        },
        {
            "OrderDate": "2022-02-08T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 1575.0,
        },
        {
            "OrderDate": "2022-02-10T00:00:00.000Z",
            "Brand": "Adidas",
            "OrderAmount": 12690.0,
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
