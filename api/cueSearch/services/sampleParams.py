SAMPLE_PARAMS = {
    "dataset": "Orders",
    "datasetId": 2,
    "datasetSql": "SELECT DATE_TRUNC('DAY', __time) as OrderDate,\n"
    "Brand, Color, State,\n"
    'SUM("count") as Orders, ROUND(sum(OrderAmount),2) as '
    "OrderAmount, sum(OrderQuantity) as OrderQuantity\n"
    "FROM FAKEORDERS\n"
    "WHERE __time >= CURRENT_TIMESTAMP - INTERVAL '13' MONTH \n"
    "GROUP BY 1, 2, 3, 4\n"
    "ORDER BY 1",
    "dimensions": ["Brand", "Color", "State"],
    "filter": "( ( Brand = 'Adidas' OR Brand = 'Nike' ) ) AND ( State = 'MS' OR "
    "State = 'KS' )",
    "filterDimensions": ["Brand", "State"],
    "granularity": "day",
    "groupedResultsForFilter": [
        [
            {
                "dataset": "Orders",
                "datasetId": 2,
                "dimension": "Brand",
                "globalDimensionName": "Brand",
                "id": 2,
                "type": "GLOBALDIMENSION",
                "user_entity_identifier": "Brand",
                "value": "Adidas",
            },
            {
                "dataset": "Orders",
                "datasetId": 2,
                "dimension": "Brand",
                "globalDimensionName": "Brand",
                "id": 2,
                "type": "GLOBALDIMENSION",
                "user_entity_identifier": "Brand",
                "value": "Nike",
            },
        ],
        [
            {
                "dataset": "Orders",
                "datasetId": 2,
                "dimension": "State",
                "globalDimensionName": "Region",
                "id": 1,
                "type": "GLOBALDIMENSION",
                "user_entity_identifier": "Region",
                "value": "MS",
            },
            {
                "dataset": "Orders",
                "datasetId": 2,
                "dimension": "State",
                "globalDimensionName": "Region",
                "id": 1,
                "type": "GLOBALDIMENSION",
                "user_entity_identifier": "Region",
                "value": "KS",
            },
        ],
    ],
    "metrics": ["Orders", "OrderAmount", "OrderQuantity"],
    "renderType": "line",
    "searchResults": [
        {
            "dataset": "Orders",
            "datasetId": 2,
            "dimension": "State",
            "globalDimensionName": "Region",
            "id": 1,
            "type": "GLOBALDIMENSION",
            "user_entity_identifier": "Region",
            "value": "MS",
        },
        {
            "dataset": "Orders",
            "datasetId": 2,
            "dimension": "State",
            "globalDimensionName": "Region",
            "id": 1,
            "type": "GLOBALDIMENSION",
            "user_entity_identifier": "Region",
            "value": "KS",
        },
        {
            "dataset": "Orders",
            "datasetId": 2,
            "dimension": "Brand",
            "globalDimensionName": "Brand",
            "id": 2,
            "type": "GLOBALDIMENSION",
            "user_entity_identifier": "Brand",
            "value": "Adidas",
        },
        {
            "dataset": "Orders",
            "datasetId": 2,
            "dimension": "Brand",
            "globalDimensionName": "Brand",
            "id": 2,
            "type": "GLOBALDIMENSION",
            "user_entity_identifier": "Brand",
            "value": "Nike",
        },
    ],
    "timestampColumn": "OrderDate",
}
