from pyspark.sql import SparkSession
from pyspark import SparkConf
import findspark

print("Loading spark packages")

findspark.init()

conf = SparkConf()

with open("spark_dependencies.txt") as file:
    lines = [line.rstrip() for line in file]
packages = ",".join(lines)

conf.set("spark.jars.packages", packages)


conf.set("spark.sql.execution.pyarrow.enabled", "true")
conf.setMaster("local[*]")


spark = SparkSession.builder.config(conf=conf).getOrCreate()
print(f"Spark Running with version {spark.version}")