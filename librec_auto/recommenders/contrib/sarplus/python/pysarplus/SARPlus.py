"""
This is the one and only (to rule them all) implementation of SAR.
"""

import logging
import pyspark.sql.functions as F
import pandas as pd
from pyspark.sql.types import (
    StringType,
    DoubleType,
    StructType,
    StructField,
    IntegerType,
    FloatType,
)
from pyspark.sql.functions import pandas_udf, PandasUDFType
from pysarplus import SARModel

SIM_COOCCUR = "cooccurrence"
SIM_JACCARD = "jaccard"
SIM_LIFT = "lift"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sarplus")


class SARPlus:
    """SAR implementation for PySpark"""

    def __init__(
        self,
        spark,
        col_user="userID",
        col_item="itemID",
        col_rating="rating",
        col_timestamp="timestamp",
        table_prefix="",
        similarity_type="jaccard",
        time_decay_coefficient=30,
        time_now=None,
        timedecay_formula=False,
        threshold=1,
    ):
        assert threshold > 0

        self.spark = spark
        self.header = {
            "col_user": col_user,
            "col_item": col_item,
            "col_rating": col_rating,
            "col_timestamp": col_timestamp,
            "prefix": table_prefix,
            "time_now": time_now,
            "time_decay_coefficient": time_decay_coefficient,
            "threshold": threshold,
        }

        self.similarity_type = similarity_type
        self.timedecay_formula = timedecay_formula

    def f(self, str, **kwargs):
        return str.format(**self.header, **kwargs)

    # denominator in time decay. Zero makes time decay irrelevant
    # toggle the computation of time decay group by formula
    # current time for time decay calculation
    # cooccurrence matrix threshold
    def fit(self, df):
        """Main fit method for SAR. Expects the dataframes to have row_id, col_id columns which are indexes,
        i.e. contain the sequential integer index of the original alphanumeric user and item IDs.
        Dataframe also contains rating and timestamp as floats; timestamp is in seconds since Epoch by default.

        Arguments:
            df (pySpark.DataFrame): input dataframe which contains the index of users and items. """

        # threshold - items below this number get set to zero in coocurrence counts

        df.createOrReplaceTempView(self.f("{prefix}df_train_input"))

        if self.timedecay_formula:
            # WARNING: previously we would take the last value in training dataframe and set it
            # as a matrix U element
            # for each user-item pair. Now with time decay, we compute a sum over ratings given
            # by a user in the case
            # when T=np.inf, so user gets a cumulative sum of ratings for a particular item and
            # not the last rating.
            # Time Decay
            # do a group by on user item pairs and apply the formula for time decay there
            # Time T parameter is in days and input time is in seconds
            # so we do dt/60/(T*24*60)=dt/(T*24*3600)
            # the folling is the query which we want to run

            query = self.f(
                """
            SELECT
                 {col_user}, {col_item}, 
                 SUM({col_rating} * EXP(-log(2) * (latest_timestamp - CAST({col_timestamp} AS long)) / ({time_decay_coefficient} * 3600 * 24))) as {col_rating}
            FROM {prefix}df_train_input,
                 (SELECT CAST(MAX({col_timestamp}) AS long) latest_timestamp FROM {prefix}df_train_input)
            GROUP BY {col_user}, {col_item} 
            CLUSTER BY {col_user} 
            """
            )

            # replace with timedecayed version
            df = self.spark.sql(query)
        else:
            # since SQL is case insensitive, this check needs to be performed similar
            if self.header["col_timestamp"].lower() in [
                s.name.lower() for s in df.schema
            ]:
                # we need to de-duplicate items by using the latest item
                query = self.f(
                    """
                SELECT {col_user}, {col_item}, {col_rating}
                FROM
                (
                SELECT
                    {col_user}, {col_item}, {col_rating}, 
                    ROW_NUMBER() OVER (PARTITION BY {col_user}, {col_item} ORDER BY {col_timestamp} DESC) latest
                FROM {prefix}df_train_input
                )
                WHERE latest = 1
                """
                )

                df = self.spark.sql(query)

        df.createOrReplaceTempView(self.f("{prefix}df_train"))

        log.info("sarplus.fit 1/2: compute item cooccurences...")

        # compute cooccurrence above minimum threshold
        query = self.f(
            """
        SELECT A.{col_item} i1, B.{col_item} i2, COUNT(*) value
        FROM   {prefix}df_train A INNER JOIN {prefix}df_train B
               ON A.{col_user} = B.{col_user} AND A.{col_item} <= b.{col_item}  
        GROUP  BY A.{col_item}, B.{col_item}
        HAVING COUNT(*) >= {threshold}
        CLUSTER BY i1, i2
        """
        )

        item_cooccurrence = self.spark.sql(query)
        item_cooccurrence.write.mode("overwrite").saveAsTable(
            self.f("{prefix}item_cooccurrence")
        )

        # compute the diagonal used later for Jaccard and Lift
        if self.similarity_type == SIM_LIFT or self.similarity_type == SIM_JACCARD:
            item_marginal = self.spark.sql(
                self.f(
                    "SELECT i1 i, value AS margin FROM {prefix}item_cooccurrence WHERE i1 = i2"
                )
            )
            item_marginal.createOrReplaceTempView(self.f("{prefix}item_marginal"))

        if self.similarity_type == SIM_COOCCUR:
            self.item_similarity = item_cooccurrence
        elif self.similarity_type == SIM_JACCARD:
            query = self.f(
                """
            SELECT i1, i2, value / (M1.margin + M2.margin - value) AS value
            FROM {prefix}item_cooccurrence A 
                INNER JOIN {prefix}item_marginal M1 ON A.i1 = M1.i 
                INNER JOIN {prefix}item_marginal M2 ON A.i2 = M2.i
            CLUSTER BY i1, i2
            """
            )
            self.item_similarity = self.spark.sql(query)
        elif self.similarity_type == SIM_LIFT:
            query = self.f(
                """
            SELECT i1, i2, value / (M1.margin * M2.margin) AS value
            FROM {prefix}item_cooccurrence A 
                INNER JOIN {prefix}item_marginal M1 ON A.i1 = M1.i 
                INNER JOIN {prefix}item_marginal M2 ON A.i2 = M2.i
            CLUSTER BY i1, i2
            """
            )
            self.item_similarity = self.spark.sql(query)
        else:
            raise ValueError(
                "Unknown similarity type: {0}".format(self.similarity_type)
            )

        # store upper triangular
        log.info(
            "sarplus.fit 2/2: compute similiarity metric %s..." % self.similarity_type
        )
        self.item_similarity.write.mode("overwrite").saveAsTable(
            self.f("{prefix}item_similarity_upper")
        )

        # expand upper triangular to full matrix

        query = self.f(
            """
        SELECT i1, i2, value
        FROM
        (
          (SELECT i1, i2, value FROM {prefix}item_similarity_upper)
          UNION ALL
          (SELECT i2 i1, i1 i2, value FROM {prefix}item_similarity_upper WHERE i1 <> i2)
        )
        CLUSTER BY i1
        """
        )

        self.item_similarity = self.spark.sql(query)
        self.item_similarity.write.mode("overwrite").saveAsTable(
            self.f("{prefix}item_similarity")
        )

        # free space
        self.spark.sql(self.f("DROP TABLE {prefix}item_cooccurrence"))
        self.spark.sql(self.f("DROP TABLE {prefix}item_similarity_upper"))

        self.item_similarity = self.spark.table(self.f("{prefix}item_similarity"))

    def get_user_affinity(self, test):
        """Prepare test set for C++ SAR prediction code.
        Find all items the test users have seen in the past.

        Arguments:
            test (pySpark.DataFrame): input dataframe which contains test users.
        """
        test.createOrReplaceTempView(self.f("{prefix}df_test"))

        query = self.f(
            "SELECT DISTINCT {col_user} FROM {prefix}df_test CLUSTER BY {col_user}"
        )

        df_test_users = self.spark.sql(query)
        df_test_users.write.mode("overwrite").saveAsTable(
            self.f("{prefix}df_test_users")
        )

        query = self.f(
            """
          SELECT a.{col_user}, a.{col_item}, CAST(a.{col_rating} AS double) {col_rating}
          FROM {prefix}df_train a INNER JOIN {prefix}df_test_users b ON a.{col_user} = b.{col_user} 
          DISTRIBUTE BY {col_user}
          SORT BY {col_user}, {col_item}          
        """
        )

        return self.spark.sql(query)

    def recommend_k_items(
        self,
        test,
        cache_path,
        top_k=10,
        remove_seen=True,
        n_user_prediction_partitions=200,
    ):

        # create item id to continuous index mapping
        log.info("sarplus.recommend_k_items 1/3: create item index")
        self.spark.sql(
            self.f(
                "SELECT i1, row_number() OVER(ORDER BY i1)-1 idx FROM (SELECT DISTINCT i1 FROM {prefix}item_similarity) CLUSTER BY i1"
            )
        ).write.mode("overwrite").saveAsTable(self.f("{prefix}item_mapping"))

        # map similarity matrix into index space
        self.spark.sql(
            self.f(
                """
            SELECT a.idx i1, b.idx i2, is.value
            FROM {prefix}item_similarity is, {prefix}item_mapping a, {prefix}item_mapping b
            WHERE is.i1 = a.i1 AND i2 = b.i1
        """
            )
        ).write.mode("overwrite").saveAsTable(self.f("{prefix}item_similarity_mapped"))

        cache_path_output = cache_path
        if cache_path.startswith("dbfs:"):
            cache_path_input = "/dbfs" + cache_path[5:]
        else:
            cache_path_input = cache_path

        # export similarity matrix for C++ backed UDF
        log.info("sarplus.recommend_k_items 2/3: prepare similarity matrix")

        self.spark.sql(
            self.f(
                "SELECT i1, i2, CAST(value AS DOUBLE) value FROM {prefix}item_similarity_mapped ORDER BY i1, i2"
            )
        ).coalesce(1).write.format("com.microsoft.sarplus").mode("overwrite").save(
            cache_path_output
        )

        self.get_user_affinity(test).createOrReplaceTempView(
            self.f("{prefix}user_affinity")
        )

        # map item ids to index space
        pred_input = self.spark.sql(
            self.f(
                """
            SELECT {col_user}, idx, rating
            FROM 
            (
                SELECT {col_user}, b.idx, {col_rating} rating
                FROM {prefix}user_affinity JOIN {prefix}item_mapping b ON {col_item} = b.i1 
            )
            CLUSTER BY {col_user}
        """
            )
        )

        schema = StructType(
            [
                StructField(
                    "userID", pred_input.schema[self.header["col_user"]].dataType, True
                ),
                StructField("itemID", IntegerType(), True),
                StructField("score", FloatType(), True),
            ]
        )

        # make sure only the header is pickled
        local_header = self.header

        # bridge to python/C++
        @pandas_udf(schema, PandasUDFType.GROUPED_MAP)
        def sar_predict_udf(df):
            # Magic happening here
            # The cache_path points to file write to by com.microsoft.sarplus
            # This has exactly the memory layout we need and since the file is
            # memory mapped, the memory consumption only happens ones per worker
            # for all python processes
            model = SARModel(cache_path_input)
            preds = model.predict(
                df["idx"].values, df["rating"].values, top_k, remove_seen
            )

            user = df[local_header["col_user"]].iloc[0]

            preds_ret = pd.DataFrame(
                [(user, x.id, x.score) for x in preds], columns=range(3)
            )

            return preds_ret

        log.info("sarplus.recommend_k_items 3/3: compute recommendations")

        df_preds = (
            pred_input.repartition(
                n_user_prediction_partitions, self.header["col_user"]
            )
            .groupby(self.header["col_user"])
            .apply(sar_predict_udf)
        )

        df_preds.createOrReplaceTempView(self.f("{prefix}predictions"))

        return self.spark.sql(
            self.f(
                """
        SELECT userID {col_user}, b.i1 {col_item}, score
        FROM {prefix}predictions p, {prefix}item_mapping b
        WHERE p.itemID = b.idx
        """
            )
        )

    def recommend_k_items_slow(self, test, top_k=10, remove_seen=True):
        """Recommend top K items for all users which are in the test set.

        Args:
            test: test Spark dataframe
            top_k: top n items to return
            remove_seen: remove items test users have already seen in the past from the recommended set.
        """

        # TODO: remove seen
        if remove_seen:
            raise ValueError("Not implemented")

        self.get_user_affinity(test).write.mode("overwrite").saveAsTable(
            self.f("{prefix}user_affinity")
        )

        # user_affinity * item_similarity
        # filter top-k
        query = self.f(
            """
        SELECT {col_user}, {col_item}, score
        FROM
        (
          SELECT df.{col_user},
                 S.i2 {col_item},
                 SUM(df.{col_rating} * S.value) AS score,
                 row_number() OVER(PARTITION BY {col_user} ORDER BY SUM(df.{col_rating} * S.value) DESC) rank
          FROM   
            {prefix}user_affinity df, 
            {prefix}item_similarity S
          WHERE df.{col_item} = S.i1
          GROUP BY df.{col_user}, S.i2
        )
        WHERE rank <= {top_k} 
        """,
            top_k=top_k,
        )

        return self.spark.sql(query)
