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

# Group those with the same course, instructor, term, and year
def combine_similar_sessions(df):
    ConcatenatedScores = StructType([
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

    def safely_get_sum(multi_vals):
        total = 0
        for val in multi_vals:
            if is_float(val):
                total += float(val)
        return total

    def safely_get_weighted_avg(multi_ratings, multi_invited):
        # Compute the total
        total = safely_get_sum(multi_invited)

        # Return the weighted average
        weighted_avg = 0
        for i in range(len(multi_ratings)):
            rating = multi_ratings[i]
            num_invited = multi_invited[i]

            if is_float(rating) and is_float(num_invited):
                weighted_avg = float(rating) * (float(num_invited) / total)

        return weighted_avg

    def concatenate_rows(cat1s, cat2s, cat3s, cat4s, cat5s, cat6s, cat7s, cat8s, cat9s, numInviteds, numRespondeds):
        total_invited = safely_get_sum(numInviteds)
        total_respondends = safely_get_sum(numRespondeds)

        total_cat_1 = safely_get_weighted_avg(cat1s, numInviteds)
        total_cat_2 = safely_get_weighted_avg(cat2s, numInviteds)
        total_cat_3 = safely_get_weighted_avg(cat3s, numInviteds)
        total_cat_4 = safely_get_weighted_avg(cat4s, numInviteds)
        total_cat_5 = safely_get_weighted_avg(cat5s, numInviteds)
        total_cat_6 = safely_get_weighted_avg(cat6s, numInviteds)
        total_cat_7 = safely_get_weighted_avg(cat7s, numInviteds)
        total_cat_8 = safely_get_weighted_avg(cat8s, numInviteds)
        total_cat_9 = safely_get_weighted_avg(cat9s, numInviteds)

        return (total_cat_1, total_cat_2, total_cat_3, total_cat_4, total_cat_5, total_cat_6, total_cat_7, total_cat_8, total_cat_9, total_invited, total_respondends)

    concatenate_rows_udf = udf(concatenate_rows, ConcatenatedScores)

    columns_to_aggregate = [collect_list(col) for col in ["cat1", "cat2", "cat3", "cat4", "cat5", "cat6", "cat7", "cat8", "cat9", "num_invited", "num_responded"]]

    # Combine the records that has the same course code, instructor, year, and term; and compute their weighted category ratings
    aggregated_data = df\
        .groupBy(df.course, df.instructor, df.year, df.term)\
        .agg(concatenate_rows_udf(*columns_to_aggregate).alias('values'))

    # Expand the "values" column to the column names in ConcatenatedScores 
    return aggregated_data.select('course', 'instructor', 'term', 'year', 'values.*')

# Uses the num_invities to explode the number of items
def explode_num_respondends(df):
    def explode_num_to_array(x):
        if is_float(x):
            x_int = int(float(x))
            return [1] * x_int
        else:
            return [1]

    n_to_array = udf(explode_num_to_array, ArrayType(IntegerType()))
    mydata1 = df.withColumn('num_responded', n_to_array(df.num_responded))

    mydata2 = mydata1.select('course', 'instructor', 'term', 'year', "cat1", "cat2", "cat3", "cat4", "cat5", "cat6", "cat7", "cat8", "cat9", explode(mydata1.num_responded))

    mydata3 = mydata2.drop('col')

    return mydata3

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
