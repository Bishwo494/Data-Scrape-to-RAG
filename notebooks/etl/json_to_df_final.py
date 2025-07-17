import pandas as pd
import json

def json_list_to_dataframe():
    #working code
    from pyspark.sql import SparkSession
    import pyspark
    import json
    from pyspark.sql import Row

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
    raw_text = spark.read.text("s3a://ebooks/random_ebooks_metadata.json")

    # Collect the data to the driver (only for small files)
    json_string = "".join([row.value for row in raw_text.collect()])

    # Find where the actual data ends (before the test data)
    end_pos = json_string.find("]\n\n[")
    if end_pos > 0:
        json_string = json_string[:end_pos + 1]

    # Parse the JSON in the driver
    parsed_data = json.loads(json_string)

    # Create DataFrame from parsed data
    df = spark.createDataFrame(parsed_data)

    # 'Title']} {row['Author']} {row['Subject']} {row['Category'

    # Now flatten the structure as before...
    final_df = df.select(
        "url",
        "title",
        F.col("about_ebook.Author").alias("author"),
        F.col("about_ebook.Title").alias("book_title"),
        F.col("about_ebook.Category").alias("Category"),
        F.col("about_ebook.Subject").alias("Subject"),
        F.col("download_links.`text/html`").alias("html_url"),
        F.coalesce(
            F.col("download_links.`text/plain; charset=us-ascii`"),
            F.col("download_links.`text/plain`")
        ).alias("text_url")
    )

    final_df.write \
    .option("header", True) \
    .mode("overwrite") \
    .csv("s3a://warehouse/golden_data/")

json_list_to_dataframe()