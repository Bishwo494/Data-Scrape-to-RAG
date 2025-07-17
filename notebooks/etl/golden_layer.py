import pandas as pd
import json

def golden_layer():
    #working code
    from pyspark.sql import SparkSession
    import pyspark
    import json
    from pyspark.sql import Row
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, concat_ws
    from pyspark.sql.types import StringType

    # === Step 1: Define Sensitive Variables ===
    NESSIE_URI = "http://nessie:19120/api/v1"
    MINIO_ENDPOINT = "http://minio:9000"
    MINIO_ACCESS_KEY = "admin"
    MINIO_SECRET_KEY = "password"
    JSON_OBJECT_URI = "s3a://ebooks/random_ebooks_metadata.json"

    # === Step 2: Spark Configuration ===
    conf = (
    pyspark.SparkConf()
    .setAppName("ReadJSONFromMinIO")

    # Required JAR packages
    .set("spark.jars.packages",
        ",".join([
            "org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.3.1",
            "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.3_2.12:0.67.0",
            "org.apache.hadoop:hadoop-aws:3.3.3",
            "com.amazonaws:aws-java-sdk-bundle:1.11.1026"
        ])
    )

    # Iceberg + Nessie
    .set("spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,"
        "org.projectnessie.spark.extensions.NessieSparkSessionExtensions")
    .set("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")
    .set("spark.sql.catalog.nessie.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog")
    .set("spark.sql.catalog.nessie.uri", NESSIE_URI)
    .set("spark.sql.catalog.nessie.ref", "main")
    .set("spark.sql.catalog.nessie.authentication.type", "NONE")
    .set("spark.sql.catalog.nessie.warehouse", "s3a://warehouse")
    .set("spark.sql.catalog.nessie.s3.endpoint", MINIO_ENDPOINT)
    .set("spark.sql.catalog.nessie.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

    # MinIO (S3A) Configuration
    .set("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
    .set("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
    .set("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
    .set("spark.hadoop.fs.s3a.path.style.access", "true")
    .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    )

    # === Step 3: Start Spark Session ===
    spark = SparkSession.builder.config(conf=conf).getOrCreate()
    print("✅ Spark Session Started")

    #Working code

    from pyspark.sql import functions as F
    import json
    # Read as text
    df_back = spark.read \
        .option("header", True) \
        .csv("s3a://warehouse/golden_data/")
   
    df2 = df_back.withColumn(
    "search_text",
        concat_ws(" ", 
                col("Title"), 
                col("Author"), 
                col("Subject"))
    )

    df2.write \
    .option("header", True) \
    .mode("overwrite") \
    .csv("s3a://warehouse/final_golden_data/")

golden_layer()