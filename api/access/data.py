from dbConnections import (
    BigQuery,
    Druid,
    Redshift,
    Snowflake,
    Druid,
    MySQL,
    Postgres,
    MSSQL,
    ClickHouse,
)
from dataset.serializers import ConnectionDetailSerializer


class Data:
    @staticmethod
    def runQueryOnConnection(connectionType, connectionParams, query, limit=True):
        dataframe = None
        if connectionType == "BigQuery":
            params = connectionParams
            dataframe = BigQuery.fetchDataframe(params, query, limit=limit)
        if connectionType == "Druid":
            params = connectionParams
            dataframe = Druid.fetchDataframe(params, query, limit=limit)
        if connectionType == "MySQL":
            params = connectionParams
            dataframe = MySQL.fetchDataframe(params, query, limit=limit)
        if connectionType == "Postgres":
            params = connectionParams
            dataframe = Postgres.fetchDataframe(params, query, limit=limit)
        if connectionType == "MSSQL":
            params = connectionParams
            dataframe = MSSQL.fetchDataframe(params, query, limit=limit)

        if connectionType == "Redshift":
            params = connectionParams
            dataframe = Redshift.fetchDataframe(params, query, limit=limit)
        if connectionType == "Snowflake":
            params = connectionParams
            dataframe = Snowflake.fetchDataframe(params, query, limit=limit)
        if connectionType == "ClickHouse":
            params = connectionParams
            dataframe = ClickHouse.fetchDataframe(params, query, limit=limit)

        return dataframe

    @staticmethod
    def fetchDatasetDataframe(dataset, customSql=None):
        connectionParams = {}
        for val in dataset.connection.cpvc.all():
            connectionParams[val.connectionParam.name] = val.value
        sql = customSql if customSql else dataset.sql
        datasetDf = Data.runQueryOnConnection(
            dataset.connection.connectionType.name,
            connectionParams,
            sql,
            False,
        )
        return datasetDf
