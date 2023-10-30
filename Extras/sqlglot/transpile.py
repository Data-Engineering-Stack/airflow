import sqlglot
t = sqlglot.transpile("SELECT EPOCH_MS(1618088028295)", read="duckdb", write="postgres")[0]

#print(callable(t))

sql = """WITH baz AS (SELECT a, c FROM foo WHERE a = 1) SELECT f.a, b.b, baz.c, CAST("b"."a" AS REAL) d FROM foo f JOIN bar b ON f.a = b.a LEFT JOIN baz ON f.a = baz.a"""
#print(sqlglot.transpile(sql, write="postgres", identify=True, pretty=True)[0])

def program(x):
            f = lambda x:x + 1
            print(callable(f))
            f(x)
program(1)
'''
from sqlglot.dialects.bigquery import BigQuery
from sqlglot.dialects.clickhouse import ClickHouse
from sqlglot.dialects.databricks import Databricks
from sqlglot.dialects.dialect import Dialect, Dialects
from sqlglot.dialects.doris import Doris
from sqlglot.dialects.drill import Drill
from sqlglot.dialects.duckdb import DuckDB
from sqlglot.dialects.hive import Hive
from sqlglot.dialects.mysql import MySQL
from sqlglot.dialects.oracle import Oracle
from sqlglot.dialects.postgres import Postgres
from sqlglot.dialects.presto import Presto
from sqlglot.dialects.redshift import Redshift
from sqlglot.dialects.snowflake import Snowflake
from sqlglot.dialects.spark import Spark
from sqlglot.dialects.spark2 import Spark2
from sqlglot.dialects.sqlite import SQLite
from sqlglot.dialects.starrocks import StarRocks
from sqlglot.dialects.tableau import Tableau
from sqlglot.dialects.teradata import Teradata
from sqlglot.dialects.trino import Trino
from sqlglot.dialects.tsql import TSQL
'''