from pyspark.sql.session import SparkSession
from pyspark import SparkContext
from pyspark.sql.types import StructType,StructField, StringType, IntegerType


sc = SparkContext("local","testsc")

spark = SparkSession \
    .builder \
    .appName("testSparkJob") \
    .getOrCreate()

spark.sparkcontext.setLogLevel("ERROR")

data2 = [("James","","Smith","36636","M",3000),
    ("Michael","Rose","","40288","M",4000),
    ("Robert","","Williams","42114","M",4000),
    ("Maria","Anne","Jones","39192","F",4000),
    ("Jen","Mary","Brown","","F",-1)
  ]

schema = StructType([ \
    StructField("firstname",StringType(),True), \
    StructField("middlename",StringType(),True), \
    StructField("lastname",StringType(),True), \
    StructField("id", StringType(), True), \
    StructField("gender", StringType(), True), \
    StructField("salary", IntegerType(), True) \
  ])

df = spark.createDataFrame(data=data2,schema=schema)
df.printSchema()
df.show(truncate=False)