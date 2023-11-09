from pyspark.sql.session import SparkSession
from pyspark import SparkContext,SparkConf
from pyspark.sql.types import StructType,StructField, StringType, IntegerType
import findspark


findspark.init()
conf= SparkConf()
print(conf)


# sc = SparkContext("local","testsc")
sc = SparkContext(appName='test-spark',conf=conf).getOrCreate()
spark = SparkSession(sc)

# conf = SparkConf().setAppName("MyApp").set("spark.executor.memory", "2g")
# sc = SparkContext(conf=conf)

# spark = SparkSession \
#     .builder \
#     .appName("testSparkJob") \
#     .getOrCreate()


data2 = [("James","","Smith","36636","M",3000),
    ("Michael","Rose","","40288","M",4000)
  ]

schema = StructType([ \
    StructField("firstname",StringType(),True), \
    StructField("middlename",StringType(),True), \
    StructField("lastname",StringType(),True), \
    StructField("id", StringType(), True), \
    StructField("gender", StringType(), True), \
    StructField("salary", IntegerType(), True) \
  ])

print("--------------------------------------> runnning from headless")

df = spark.createDataFrame(data=data2,schema=schema)
df.printSchema()
df.show()