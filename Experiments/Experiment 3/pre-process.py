from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import *
from pyspark import SparkConf, SparkContext

from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, OneHotEncoderEstimator

import re

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

    def get_instructor_name(firstname, lastname):
        firstname = firstname.strip()
        lastname = lastname.strip()

        if len(firstname) > 0 and len(lastname) > 0:
            return lastname + ', ' + firstname[0] + '.'
        return ''

    get_instructor_name_udf = udf(get_instructor_name, StringType())
    df = df.withColumn('instructor', get_instructor_name_udf(df.firstname, df.lastname))

    # Take only records with first and last name
    df = df.filter(col("instructor") != "")

    # Drop the "firstname" and "lastname" column
    df = df.drop("lastname").drop("firstname")

    return df

# Perform one hot encoding on courses and instructors
def encode_courses_and_instructors(df):
    course_string_indexer = StringIndexer(inputCol="course", outputCol="course_index")
    instructor_string_indexer = StringIndexer(inputCol="instructor", outputCol="instructor_index")

    encoder = OneHotEncoderEstimator(inputCols=["course_index", "instructor_index"],
                                     outputCols=["course_vec", "instructor_vec"])
    encoder.setDropLast(False)

    pipeline = Pipeline(stages=[course_string_indexer, instructor_string_indexer])

    indexed_data = pipeline.fit(df).transform(df)

    # Make a table mapping course index and course name
    courses_table = indexed_data.select('course_index', 'course').distinct()

    # Make a table mapping instructor index and instructor name
    instructors_table = indexed_data.select('instructor_index', 'instructor').distinct()

    indexed_data = indexed_data.select('course_index', 'instructor_index', 'term', 'year', "cat1", "cat2", "cat3", "cat4", "cat5", "cat6", "cat7", "cat8", "cat9", "num_invited", "num_responded")

    return indexed_data, courses_table, instructors_table

# Remove rows with null values
def remove_all_null_values(df):

    # Take in those that have a positive num_respondent count and a reasonable cat8 value
    def is_valid(cat1_val, cat2_val, cat3_val, cat4_val, cat5_val, cat6_val, cat7_val, cat8_val, num_respondends):
        cat_vals = [cat1_val, cat2_val, cat3_val, cat4_val, cat5_val, cat6_val, cat7_val, cat8_val]

        for cat_val in cat_vals:
            if not is_float(cat_val):
                return False

            cat_val_float = float(cat_val)
            if not (0 <= cat_val_float <= 5):
                return False

        if is_float(num_respondends):
            num_respondends_int = int(float(num_respondends))

            return num_respondends_int > 0

        return False

    is_valid_udf = udf(is_valid, BooleanType())
    df = df.withColumn('is_valid', is_valid_udf(df.cat1, df.cat2, df.cat3, df.cat4, df.cat5, df.cat6, df.cat7, df.cat8, df.num_responded))
    df = df.filter(df.is_valid == True)

    df = df.drop("is_valid")

    return df

if __name__ == "__main__":
    spark = SparkSession.builder.master("local").appName("My App").getOrCreate()

    raw_data = spark.read \
        .format("csv") \
        .option("sep", ",") \
        .option("header", "true") \
        .schema(RawRecord) \
        .load("raw-data.csv")

    mydata = raw_data\
        .filter(raw_data.dept != "N/A")\
        .filter(raw_data.course != "N/A")\
        .filter(raw_data.lastname != "N/A")\
        .filter(raw_data.firstname != "N/A")\
        .filter(raw_data.term != "N/A")\
        .filter(raw_data.year != "N/A")

    mydata2 = parse_course_codes(mydata)
    mydata3 = mydata2.drop("dept").drop("division")
    mydata7 = regroup_instructors_name(mydata3)
    mydata8 = remove_all_null_values(mydata7)

    mydata8.repartition(1).write.format("csv").option("header", "true").save('clean-data')
