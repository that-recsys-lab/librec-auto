# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import pytest
import pandas as pd
from pandas.util.testing import assert_frame_equal

try:
    from pyspark.sql import Row
    from reco_utils.evaluation.spark_diversity_evaluation import DiversityEvaluation
except ImportError:    
    pass  # skip this import if we are in pure python environment

TOL = 0.0001

@pytest.fixture(scope="module")
def target_metrics():
    return {
        "c_coverage": pytest.approx(0.8, TOL),
        "d_coverage": pytest.approx(0.76732, TOL),
        "item_novelty": pd.DataFrame(
        dict(ItemId=[1, 2, 3, 5], item_novelty=[1.0, 0.0, 0.0, 0.0])
        ),
        "user_novelty": pd.DataFrame(
        dict(UserId=[1, 2, 3], user_novelty=[0.0, 0.0, 0.5])
        ),
        "novelty": pd.DataFrame(
        dict(novelty=[0.16667])
        ),
        "diversity": pd.DataFrame(
        dict(diversity=[0.43096])
        ),
        "user_diversity": pd.DataFrame(
        dict(UserId=[1, 2, 3], user_diversity=[0.29289, 1.0, 0.0])
        ),
        "user_item_serendipity": pd.DataFrame(
        dict(UserId=[1, 1, 2, 2, 3, 3], ItemId= [3, 5, 2, 5, 1, 2], user_item_serendipity=[0.72783, 0.80755, 0.71132, 0.35777, 0.80755, 0.80755])
        ),
        "user_serendipity": pd.DataFrame(
        dict(UserId=[1, 2, 3], user_serendipity=[0.76770, 0.53455, 0.80755])
        ),
        "serendipity": pd.DataFrame(
        dict(serendipity=[0.70326])
        ),
    }

@pytest.fixture(scope="module")
def spark_data(spark):
    train_df = spark.createDataFrame([
      Row(UserId=1, ItemId=1),
      Row(UserId=1, ItemId=2),
      Row(UserId=1, ItemId=4),
      Row(UserId=2, ItemId=3),
      Row(UserId=2, ItemId=4),
      Row(UserId=3, ItemId=3),
      Row(UserId=3, ItemId=4),
      Row(UserId=3, ItemId=5),  
    ])
    reco_df = spark.createDataFrame([
      Row(UserId=1, ItemId=3, Rating=1),
      Row(UserId=1, ItemId=5, Rating=1),
      Row(UserId=2, ItemId=2, Rating=1),
      Row(UserId=2, ItemId=5, Rating=1),
      Row(UserId=3, ItemId=1, Rating=1),
      Row(UserId=3, ItemId=2, Rating=1),  
    ])
    return train_df, reco_df
    
@pytest.mark.spark
def test_catalog_coverage(spark_data, target_metrics):
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId')
    c_coverage = evaluator.catalog_coverage()
    assert c_coverage == target_metrics["c_coverage"]
    
@pytest.mark.spark
def test_distributional_coverage(spark_data, target_metrics):
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId')
    d_coverage = evaluator.distributional_coverage()
    assert d_coverage == target_metrics["d_coverage"]

@pytest.mark.spark
def test_item_novelty(spark_data, target_metrics):
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId')
    actual = evaluator.item_novelty().toPandas()
    assert_frame_equal(target_metrics["item_novelty"], actual, check_exact=False, check_less_precise=4)

@pytest.mark.spark    
def test_user_novelty(spark_data, target_metrics):
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId')
    actual = evaluator.user_novelty().toPandas()
    assert_frame_equal(target_metrics["user_novelty"], actual, check_exact=False, check_less_precise=4)

@pytest.mark.spark    
def test_novelty(spark_data, target_metrics):
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId')
    actual = evaluator.novelty().toPandas()
    assert_frame_equal(target_metrics["novelty"], actual, check_exact=False, check_less_precise=4)

@pytest.mark.spark    
def test_user_diversity(spark_data, target_metrics):
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId')
    actual = evaluator.user_diversity().toPandas()
    assert_frame_equal(target_metrics["user_diversity"], actual, check_exact=False, check_less_precise=4)

@pytest.mark.spark    
def test_diversity(spark_data, target_metrics):   
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId') 
    actual = evaluator.diversity().toPandas()
    assert_frame_equal(target_metrics["diversity"], actual,check_exact=False, check_less_precise=4)   

@pytest.mark.spark    
def test_user_item_serendipity(spark_data, target_metrics):
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId')
    actual = evaluator.user_item_serendipity().toPandas()
    assert_frame_equal(target_metrics["user_item_serendipity"], actual, check_exact=False, check_less_precise=4)

@pytest.mark.spark    
def test_user_serendipity(spark_data, target_metrics):
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId')
    actual = evaluator.user_serendipity().toPandas()
    assert_frame_equal(target_metrics["user_serendipity"], actual, check_exact=False, check_less_precise=4)

@pytest.mark.spark    
def test_serendipity(spark_data, target_metrics):
    train_df, reco_df = spark_data  
    evaluator = DiversityEvaluation(train_df=train_df, reco_df=reco_df,
                         col_user='UserId', col_item='ItemId')
    actual = evaluator.serendipity().toPandas()
    assert_frame_equal(target_metrics["serendipity"], actual, check_exact=False, check_less_precise=4)
