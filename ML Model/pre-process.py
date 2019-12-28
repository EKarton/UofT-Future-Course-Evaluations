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

# Get the department (not use the default dept from the data since it is wrong)
def parse_dept(df):
    def get_dept_from_course_code(course_code):
        return course_code[:3]

    get_dept_from_course_code_udf = udf(get_dept_from_course_code)
    df = df.withColumn('dept', get_dept_from_course_code_udf(df.course))

    return df

# Make the instructors col and remove the firstname and lastname column
def regroup_instructors_name(df):

    def get_instructor_name(firstname, lastname):
        firstname = firstname.strip()
        lastname = lastname.strip()

        if len(firstname) > 0 and len(lastname) > 0:
            return firstname + ' ' + lastname

        return ''

    def get_abbrev_instructor_name(firstname, lastname):
        firstname = firstname.strip()
        lastname = lastname.strip()

        if len(firstname) > 0 and len(lastname) > 0:
            return lastname + ' ' + firstname[0]

        return ''

    get_instructor_name_udf = udf(get_instructor_name)
    get_abbrev_instructor_name_udf = udf(get_abbrev_instructor_name)

    df = df.withColumn('abbrev_instructor', get_abbrev_instructor_name_udf(df.firstname, df.lastname))
    df = df.withColumn('instructor', get_instructor_name_udf(df.firstname, df.lastname))

    # Drop the lastname and firstname column
    df = df.drop('firstname').drop('lastname')

    return df

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
    mydata3 = parse_dept(mydata2)
    mydata4 = mydata3.drop('division')
    mydata7 = regroup_instructors_name(mydata4)
    mydata8 = remove_all_null_values(mydata7)

    # instructor_name_mappings = get_abbrev_instructor_name_mappings(mydata8)

    # Dump the csv file just for the ML model
    mydata8 \
        .select('course', 'instructor', 'cat1', 'cat2', 'cat3', 'cat4', 'cat5', 'cat6', 'cat7', 'cat8', 'cat9') \
        .repartition(1).write.format("csv").option("header", "true").save('clean-data')

    # Dump the csv file just for the instructors mapping
    mydata8 \
        .select('dept', 'course', 'instructor', 'abbrev_instructor') \
        .repartition(1).write.format("csv").option("header", "true").save('instructor-name-mappings')
