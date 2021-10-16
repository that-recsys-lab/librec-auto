import pandas as pd
import numpy as np
from pyspark.ml.recommendation import ALS
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import FloatType, IntegerType, LongType
from fastai.collab import collab_learner, CollabDataBunch
import surprise
import cornac

from reco_utils.common.constants import (
    COL_DICT,
    DEFAULT_K,
    DEFAULT_USER_COL,
    DEFAULT_ITEM_COL,
    DEFAULT_RATING_COL,
    DEFAULT_PREDICTION_COL,
    DEFAULT_TIMESTAMP_COL,
    SEED,
)
from reco_utils.common.timer import Timer
from reco_utils.common.spark_utils import start_or_get_spark
from reco_utils.recommender.sar.sar_singlenode import SARSingleNode
from reco_utils.recommender.ncf.ncf_singlenode import NCF
from reco_utils.recommender.ncf.dataset import Dataset as NCFDataset
from reco_utils.recommender.surprise.surprise_utils import (
    predict,
    compute_ranking_predictions,
)
from reco_utils.recommender.fastai.fastai_utils import (
    cartesian_product,
    score,
)
from reco_utils.recommender.cornac.cornac_utils import predict_ranking
from reco_utils.recommender.deeprec.models.graphrec.lightgcn import LightGCN
from reco_utils.recommender.deeprec.DataModel.ImplicitCF import ImplicitCF
from reco_utils.recommender.deeprec.deeprec_utils import prepare_hparams
from reco_utils.evaluation.spark_evaluation import (
    SparkRatingEvaluation,
    SparkRankingEvaluation,
)
from reco_utils.evaluation.python_evaluation import (
    map_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)
from reco_utils.evaluation.python_evaluation import (
    rmse,
    mae,
    rsquared,
    exp_var
)


def prepare_training_als(train, test):
    schema = StructType(
        (
            StructField(DEFAULT_USER_COL, IntegerType()),
            StructField(DEFAULT_ITEM_COL, IntegerType()),
            StructField(DEFAULT_RATING_COL, FloatType()),
            StructField(DEFAULT_TIMESTAMP_COL, LongType()),
        )
    )
    spark = start_or_get_spark()
    return spark.createDataFrame(train, schema)


def train_als(params, data):
    symbol = ALS(**params)
    with Timer() as t:
        model = symbol.fit(data)
    return model, t


def prepare_metrics_als(train, test):
    schema = StructType(
        (
            StructField(DEFAULT_USER_COL, IntegerType()),
            StructField(DEFAULT_ITEM_COL, IntegerType()),
            StructField(DEFAULT_RATING_COL, FloatType()),
            StructField(DEFAULT_TIMESTAMP_COL, LongType()),
        )
    )
    spark = start_or_get_spark()
    return spark.createDataFrame(train, schema), spark.createDataFrame(test,
                                                                       schema)


def predict_als(model, test):
    with Timer() as t:
        preds = model.transform(test)
    return preds, t


def recommend_k_als(model, test, train, top_k=DEFAULT_K, remove_seen=True):
    with Timer() as t:
        # Get the cross join of all user-item pairs and score them.
        users = train.select(DEFAULT_USER_COL).distinct()
        items = train.select(DEFAULT_ITEM_COL).distinct()
        user_item = users.crossJoin(items)
        dfs_pred = model.transform(user_item)

        # Remove seen items
        dfs_pred_exclude_train = dfs_pred.alias("pred").join(
            train.alias("train"),
            (dfs_pred[DEFAULT_USER_COL] == train[DEFAULT_USER_COL])
            & (dfs_pred[DEFAULT_ITEM_COL] == train[DEFAULT_ITEM_COL]),
            how="outer",
        )
        topk_scores = dfs_pred_exclude_train.filter(
            dfs_pred_exclude_train["train." + DEFAULT_RATING_COL].isNull()
        ).select(
            "pred." + DEFAULT_USER_COL,
            "pred." + DEFAULT_ITEM_COL,
            "pred." + DEFAULT_PREDICTION_COL,
        )
    return topk_scores, t


def prepare_training_svd(train, test):
    reader = surprise.Reader("ml-100k", rating_scale=(1, 5))
    return surprise.Dataset.load_from_df(
        train.drop(DEFAULT_TIMESTAMP_COL, axis=1), reader=reader
    ).build_full_trainset()


def train_svd(params, data):
    model = surprise.SVD(**params)
    with Timer() as t:
        model.fit(data)
    return model, t


def predict_svd(model, test):
    with Timer() as t:
        preds = predict(
            model,
            test,
            usercol=DEFAULT_USER_COL,
            itemcol=DEFAULT_ITEM_COL,
            predcol=DEFAULT_PREDICTION_COL,
        )
    return preds, t


def recommend_k_svd(model, test, train, top_k=DEFAULT_K, remove_seen=True):
    with Timer() as t:
        topk_scores = compute_ranking_predictions(
            model,
            train,
            usercol=DEFAULT_USER_COL,
            itemcol=DEFAULT_ITEM_COL,
            predcol=DEFAULT_PREDICTION_COL,
            remove_seen=remove_seen,
        )
    return topk_scores, t


def prepare_training_fastai(train, test):
    data = train.copy()
    data[DEFAULT_USER_COL] = data[DEFAULT_USER_COL].astype("str")
    data[DEFAULT_ITEM_COL] = data[DEFAULT_ITEM_COL].astype("str")
    data = CollabDataBunch.from_df(
        data,
        user_name=DEFAULT_USER_COL,
        item_name=DEFAULT_ITEM_COL,
        rating_name=DEFAULT_RATING_COL,
        valid_pct=0,
    )
    return data


def train_fastai(params, data):
    model = collab_learner(
        data,
        n_factors=params["n_factors"],
        y_range=params["y_range"],
        wd=params["wd"]
    )
    with Timer() as t:
        model.fit_one_cycle(cyc_len=params["epochs"], max_lr=params["max_lr"])
    return model, t


def prepare_metrics_fastai(train, test):
    data = test.copy()
    data[DEFAULT_USER_COL] = data[DEFAULT_USER_COL].astype("str")
    data[DEFAULT_ITEM_COL] = data[DEFAULT_ITEM_COL].astype("str")
    return train, data


def predict_fastai(model, test):
    with Timer() as t:
        preds = score(
            model,
            test_df=test,
            user_col=DEFAULT_USER_COL,
            item_col=DEFAULT_ITEM_COL,
            prediction_col=DEFAULT_PREDICTION_COL,
        )
    return preds, t


def recommend_k_fastai(model, test, train, top_k=DEFAULT_K, remove_seen=True):
    with Timer() as t:
        total_users, total_items = model.data.train_ds.x.classes.values()
        total_items = total_items[1:]
        total_users = total_users[1:]
        test_users = test[DEFAULT_USER_COL].unique()
        test_users = np.intersect1d(test_users, total_users)
        users_items = cartesian_product(test_users, total_items)
        users_items = pd.DataFrame(
            users_items, columns=[DEFAULT_USER_COL, DEFAULT_ITEM_COL]
        )
        training_removed = pd.merge(
            users_items,
            train.astype(str),
            on=[DEFAULT_USER_COL, DEFAULT_ITEM_COL],
            how="left",
        )
        training_removed = training_removed[
            training_removed[DEFAULT_RATING_COL].isna()
        ][[DEFAULT_USER_COL, DEFAULT_ITEM_COL]]
        topk_scores = score(
            model,
            test_df=training_removed,
            user_col=DEFAULT_USER_COL,
            item_col=DEFAULT_ITEM_COL,
            prediction_col=DEFAULT_PREDICTION_COL,
            top_k=top_k,
        )
    return topk_scores, t


def prepare_training_ncf(train, test):
    return NCFDataset(
        train=train,
        col_user=DEFAULT_USER_COL,
        col_item=DEFAULT_ITEM_COL,
        col_rating=DEFAULT_RATING_COL,
        col_timestamp=DEFAULT_TIMESTAMP_COL,
        seed=SEED,
    )


def train_ncf(params, data):
    model = NCF(n_users=data.n_users, n_items=data.n_items, **params)
    with Timer() as t:
        model.fit(data)
    return model, t


def recommend_k_ncf(model, test, train, top_k=DEFAULT_K, remove_seen=True):
    with Timer() as t:
        users, items, preds = [], [], []
        item = list(train[DEFAULT_ITEM_COL].unique())
        for user in train[DEFAULT_USER_COL].unique():
            user = [user] * len(item)
            users.extend(user)
            items.extend(item)
            preds.extend(list(model.predict(user, item, is_list=True)))
        topk_scores = pd.DataFrame(
            data={
                DEFAULT_USER_COL: users,
                DEFAULT_ITEM_COL: items,
                DEFAULT_PREDICTION_COL: preds,
            }
        )
        merged = pd.merge(
            train,
            topk_scores,
            on=[DEFAULT_USER_COL, DEFAULT_ITEM_COL],
            how="outer"
        )
        topk_scores = merged[merged[DEFAULT_RATING_COL].isnull()].drop(
            DEFAULT_RATING_COL, axis=1
        )
    return topk_scores, t


def prepare_training_cornac(train, test):
    return cornac.data.Dataset.from_uir(
        train.drop(DEFAULT_TIMESTAMP_COL, axis=1).itertuples(index=False),
        seed=SEED
    )


def recommend_k_cornac(model, test, train, top_k=DEFAULT_K, remove_seen=True):
    with Timer() as t:
        topk_scores = predict_ranking(
            model,
            train,
            usercol=DEFAULT_USER_COL,
            itemcol=DEFAULT_ITEM_COL,
            predcol=DEFAULT_PREDICTION_COL,
            remove_seen=remove_seen,
        )
    return topk_scores, t


def train_bpr(params, data):
    model = cornac.models.BPR(**params)
    with Timer() as t:
        model.fit(data)
    return model, t


def train_bivae(params, data):
    model = cornac.models.BiVAECF(**params)
    with Timer() as t:
        model.fit(data)
    return model, t


def prepare_training_sar(train, test):
    return train


def train_sar(params, data):
    model = SARSingleNode(**params)
    model.set_index(data)
    with Timer() as t:
        model.fit(data)
    return model, t


def recommend_k_sar(model, test, train, top_k=DEFAULT_K, remove_seen=True):
    with Timer() as t:
        topk_scores = model.recommend_k_items(
            test, top_k=top_k, remove_seen=remove_seen
        )
    return topk_scores, t


def prepare_training_lightgcn(train, test):
    return ImplicitCF(train=train, test=test)


def train_lightgcn(params, data):
    hparams = prepare_hparams(**params)
    model = LightGCN(hparams, data)
    with Timer() as t:
        model.fit()
    return model, t


def recommend_k_lightgcn(model,
                         test,
                         train,
                         top_k=DEFAULT_K,
                         remove_seen=True):
    with Timer() as t:
        topk_scores = model.recommend_k_items(
            test, top_k=top_k, remove_seen=remove_seen
        )
    return topk_scores, t


def rating_metrics_pyspark(test, predictions):
    rating_eval = SparkRatingEvaluation(test, predictions, **COL_DICT)
    return {
        "RMSE": rating_eval.rmse(),
        "MAE": rating_eval.mae(),
        "R2": rating_eval.exp_var(),
        "Explained Variance": rating_eval.rsquared(),
    }


def ranking_metrics_pyspark(test, predictions, k=DEFAULT_K):
    rank_eval = SparkRankingEvaluation(
        test, predictions, k=k, relevancy_method="top_k", **COL_DICT
    )
    return {
        "MAP": rank_eval.map_at_k(),
        "nDCG@k": rank_eval.ndcg_at_k(),
        "Precision@k": rank_eval.precision_at_k(),
        "Recall@k": rank_eval.recall_at_k(),
    }


def rating_metrics_python(test, predictions):
    return {
        "RMSE": rmse(test, predictions, **COL_DICT),
        "MAE": mae(test, predictions, **COL_DICT),
        "R2": rsquared(test, predictions, **COL_DICT),
        "Explained Variance": exp_var(test, predictions, **COL_DICT),
    }


def ranking_metrics_python(test, predictions, k=DEFAULT_K):
    return {
        "MAP": map_at_k(test, predictions, k=k, **COL_DICT),
        "nDCG@k": ndcg_at_k(test, predictions, k=k, **COL_DICT),
        "Precision@k": precision_at_k(test, predictions, k=k, **COL_DICT),
        "Recall@k": recall_at_k(test, predictions, k=k, **COL_DICT),
    }
