import json
import logging
import pandas as pd
from psycopg2 import connect
from .constants import LIMIT

logger = logging.getLogger(__name__)


class Postgres:
    """
    Class to support functionalities on MySQL connection
    """

    def checkConnection(params):
        res = True
        try:
            host = params.get("host", "")
            port = int(params.get("port", 25060))
            database = params.get("database", "")
            user = params.get("username", "")
            password = params.get("password", "")
            conn = connect(
                host=host, port=port, database=database, user=user, password=password
            )
            curs = conn.cursor()

        except Exception as ex:
            logger.error("Can't connect to db with this credentials ")
            res = False
        return res

    def fetchDataframe(params: str, sql: str, limit: bool = False):
        dataframe = None
        try:
            host = params.get("host", "")
            port = int(params.get("port", 25060))
            database = params.get("database", "")
            user = params.get("username", "")
            password = params.get("password", "")
            conn = connect(
                host=host, port=port, database=database, user=user, password=password
            )
            curs = conn.cursor()
            if limit:
                chunksize = LIMIT
                dataframes = pd.read_sql(sql, conn, chunksize=chunksize)
                for dataframe in dataframes:
                    break
            else:
                dataframe = pd.read_sql(sql, conn)

        except Exception as ex:
            logger.error("Can't connect to db with this credentials %s", str(ex))

        return dataframe
