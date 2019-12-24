from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import *
from pyspark import SparkConf, SparkContext

from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, OneHotEncoderEstimator

import re

spark = SparkSession.builder.master("local").appName("My App").getOrCreate()

RawRecord = StructType([
    StructField("dept", StringType(), True),
    StructField("division", StringType(), True),
    StructField("course", StringType(), True),
    StructField("lastname", StringType(), True),
    StructField("firstname", StringType(), True),
    StructField("term", StringType(), True),
    StructField("year", StringType(), True),
    StructField("cat1", StringType(), True),
    StructField("cat2", StringType(), True),
    StructField("cat3", StringType(), True),
    StructField("cat4", StringType(), True),
    StructField("cat5", StringType(), True),
    StructField("cat6", StringType(), True),
    StructField("cat7", StringType(), True),
    StructField("cat8", StringType(), True),
    StructField("cat9", StringType(), True),
    StructField("num_invited", StringType(), True),
    StructField("num_responded", StringType(), True)])

raw_data = spark.read \
    .format("csv") \
    .option("sep", ",") \
    .option("header", "true") \
    .schema(RawRecord) \
    .load("data.csv")

mydata = raw_data\
    .filter(raw_data.dept != "N/A")\
    .filter(raw_data.course != "N/A")\
    .filter(raw_data.lastname != "N/A")\
    .filter(raw_data.firstname != "N/A")\
    .filter(raw_data.term != "N/A")\
    .filter(raw_data.year != "N/A")

def is_float(s):
    try: 
        float(s)
        return True

    except ValueError:
        return False

# Replace each cell in the course column with the course code
def parse_course_codes(df):
    def getCourseCode(x):
        if x is None:
            return "N/A"
        match = re.search("[A-Z]{3}\\d{3}[A-Z]\\d", x)
        if match is None:
            return "N/A"
        return match.group()

    toCourseCodeColumn = udf(getCourseCode)

    # Convert course names to only course codes
    temp = df.withColumn("course", toCourseCodeColumn(col("course")))

    # Take only records with course codes
    return temp.filter(col("course") != "N/A")

# Make the instructors col and remove the firstname and lastname column
def regroup_instructors_name(df):
    # Trim the endpoints of the first and last name
    mydata4 = df\
        .withColumn("firstname", trim(col("firstname")))\
        .withColumn("lastname", trim(col("lastname")))

    # Take only records with first and last name
    mydata4 = mydata4.filter((col("firstname") != "") & (col("lastname") != ""))

    # Concatenate the first and last name
    mydata5 = mydata4.withColumn("firstname", concat(col("firstname"), lit(" "), col("lastname")))

    # Rename the firstname column to instructors
    mydata6 = mydata5.withColumnRenamed("firstname", "instructor")

    # Drop the "lastname" column
    return mydata6.drop("lastname")

mydata2 = parse_course_codes(mydata)
mydata3 = mydata2.drop("dept").drop("division")
df = regroup_instructors_name(mydata3)

# Priority #1: Maps average from all courses the instructor has taught
instructor_rating_avg = None

# Priority #2: Maps average from all instructors
instructor_rating_avg_avg = None

# Priority #1: Maps average from 
course_rating_avg = None

# Priority #2
dept_rating_avg = None

# Priority #3

'''
    This is bad. Turns out that accuracy is max. 0.6
    If we omit the records with null values, we get an accuracy of 0.63 (much higher)
'''

def get_category_value(cat_val):
    if is_float(cat_val):
        return float(cat_val)
    return 3.0

get_category_value_udf = udf(get_category_value, DoubleType())
df = df.withColumn('cat1', get_category_value_udf(df.cat1))
df = df.withColumn('cat2', get_category_value_udf(df.cat2))
df = df.withColumn('cat3', get_category_value_udf(df.cat3))
df = df.withColumn('cat4', get_category_value_udf(df.cat4))
df = df.withColumn('cat5', get_category_value_udf(df.cat5))
df = df.withColumn('cat6', get_category_value_udf(df.cat6))
df = df.withColumn('cat7', get_category_value_udf(df.cat7))
df = df.withColumn('cat8', get_category_value_udf(df.cat8))
df = df.withColumn('cat9', get_category_value_udf(df.cat9))


df.repartition(1).write.format("csv").option("header", "true").save('output')