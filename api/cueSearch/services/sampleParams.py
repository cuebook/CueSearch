SAMPLE_PARAMS = {
    "datasetId": 1,
    "searchResults": [
        {
            "value": "BR",
            "dimension": "DeliveryRegion",
            "globalDimensionName": "Data8",
            "user_entity_identifier": "Data8",
            "id": 8,
            "dataset": "Test data",
            "datasetId": 1,
            "type": "GLOBALDIMENSION"
        },
        {
            "value": "GA",
            "dimension": "DeliveryRegion",
            "globalDimensionName": "Data8",
            "user_entity_identifier": "Data8",
            "id": 8,
            "dataset": "Test data",
            "datasetId": 1,
            "type": "GLOBALDIMENSION"
        },
        {
            "value": "KA",
            "dimension": "DeliveryRegion",
            "globalDimensionName": "Data8",
            "user_entity_identifier": "Data8",
            "id": 8,
            "dataset": "Test data",
            "datasetId": 1,
            "type": "GLOBALDIMENSION"
        },
        {
            "value": "MH",
            "dimension": "DeliveryRegion",
            "globalDimensionName": "Data8",
            "user_entity_identifier": "Data8",
            "id": 8,
            "dataset": "Test data",
            "datasetId": 1,
            "type": "GLOBALDIMENSION"
        }
    ],
    "groupedResultsForFilter": [
        [
            {
                "value": "BR",
                "dimension": "DeliveryRegion",
                "globalDimensionName": "Data8",
                "user_entity_identifier": "Data8",
                "id": 8,
                "dataset": "Test data",
                "datasetId": 1,
                "type": "GLOBALDIMENSION"
            },
            {
                "value": "GA",
                "dimension": "DeliveryRegion",
                "globalDimensionName": "Data8",
                "user_entity_identifier": "Data8",
                "id": 8,
                "dataset": "Test data",
                "datasetId": 1,
                "type": "GLOBALDIMENSION"
            },
            {
                "value": "KA",
                "dimension": "DeliveryRegion",
                "globalDimensionName": "Data8",
                "user_entity_identifier": "Data8",
                "id": 8,
                "dataset": "Test data",
                "datasetId": 1,
                "type": "GLOBALDIMENSION"
            },
            {
                "value": "MH",
                "dimension": "DeliveryRegion",
                "globalDimensionName": "Data8",
                "user_entity_identifier": "Data8",
                "id": 8,
                "dataset": "Test data",
                "datasetId": 1,
                "type": "GLOBALDIMENSION"
            }
        ]
    ],
    "filter": "( DeliveryRegion = 'Delhi' OR DeliveryRegion = 'Goa' OR DeliveryRegion = 'Maharastra' OR DeliveryRegion = 'Karnataka' )",
    "filterDimensions": [
        "DeliveryRegion"
    ],
    "renderType": "table",
    "dataset": "Test data",
    "dimensions": [
        "DeliveryRegion",
        "Brand",
        "WarehouseCode"
    ],
    "metrics": [
        "ReturnEntries",
        "RefundAmount"
    ],
    "timestampColumn": "ReturnDate",
    "datasetSql": "SELECT DATE_TRUNC('DAY', __time) as ReturnDate,\nDeliveryRegionCode as DeliveryRegion, P_BRANDCODE as Brand, WarehouseCode,\nSUM(\"count\") as ReturnEntries, sum(P_FINALREFUNDAMOUNT) as RefundAmount\nFROM RETURNENTRY\nWHERE __time >= CURRENT_TIMESTAMP - INTERVAL '13' MONTH \nGROUP BY 1, 2, 3, 4\nORDER BY 1",
    "granularity": "day",
}
