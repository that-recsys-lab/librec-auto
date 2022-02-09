#Created by: Zijun Liu
#File: Deep Learning Recommendation Algorithm
#CIKM 2021
#Last modified by: Jessie J. Smith
#February 2022
#Added wide and deep algorithm

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
import os
import scrapbook as sb
tf.get_logger().setLevel('ERROR') # only show error messages

from librec_auto.core import read_config_file
from librec_auto.core.util.xml_utils import single_xpath

# from recommenders.reco_utils.recommender.cornac.cornac_utils import predict_ranking
from recommenders.utils.constants import (
    DEFAULT_USER_COL as USER_COL,
    DEFAULT_ITEM_COL as ITEM_COL,
    DEFAULT_RATING_COL as RATING_COL,
    DEFAULT_PREDICTION_COL as PREDICT_COL,
    SEED
)
from tempfile import TemporaryDirectory
from recommenders.utils import tf_utils, gpu_utils, plot
from recommenders.datasets import movielens
from recommenders.datasets.pandas_df_utils import user_item_pairs
from recommenders.datasets.python_splitters import python_random_split
import recommenders.evaluation.python_evaluation as evaluator
import recommenders.models.wide_deep.wide_deep_utils as wide_deep
from recommenders.datasets.sparse import AffinityMatrix
from recommenders.models.vae.standard_vae import StandardVAE
from recommenders.datasets.python_splitters import numpy_stratified_split
from recommenders.utils.python_utils import binarize

def read_args():
    parser = argparse.ArgumentParser(description='nnRec')
    parser.add_argument('conf', help='Name of configuration file')
    parser.add_argument('train', help='Path to training data file')
    parser.add_argument('test', help='Path to test data file')
    parser.add_argument('result', help='Path to destination results file')
    parser.add_argument('model', help='Path to temporary model file')
    parser.add_argument('--model_type', choices=['StandardVAE', 'wide_deep'],
                        default='StandardVAE')
    # -- Arguments for StandardVAE --
    parser.add_argument('--max_len', type=int, default=10)
    parser.add_argument('--LATENT_DIM', type=int, default=50)
    parser.add_argument('--ENCODER_DIMS', type=int, default=100)
    parser.add_argument('--INTERMEDIATE_DIM', type=str, default=200)
    parser.add_argument('--NUM_EPOCHS', type=int, default=500)
    # parser.add_argument('--BATCH_SIZE', type=int, default=128)
    parser.add_argument('--HOLDOUT_PCT', type=int, default=10)
    parser.add_argument('--BINARIZATION_THRESHOLD', type=float, default=3.5)

    # -- Hyperparams for Wide and Deep --
    parser.add_argument('--EVAL_WHILE_TRAINING', type=bool, default=True)
    parser.add_argument('--STEPS', type=int, default=50000) #number of batches to train
    parser.add_argument('--BATCH_SIZE', type=int, default=32)
    # -- Hyperparams for Wide (linear) model --
    parser.add_argument('--LINEAR_OPTIMIZER', type=str, default='adagrad')
    parser.add_argument('--LINEAR_OPTIMIZER_LR', type=float, default=0.0621)  # Learning rate
    parser.add_argument('--LINEAR_L1_REG', type=float, default=0.0)  # Regularization rate for FtrlOptimizer
    parser.add_argument('--LINEAR_L2_REG', type=float, default=0.0)
    parser.add_argument('--LINEAR_MOMENTUM', type=float, default=0.0)  # Momentum for MomentumOptimizer or RMSPropOptimizer
    # -- Hyperparams for DNN model --
    parser.add_argument('--DNN_OPTIMIZER', type=str, default='adadelta')
    parser.add_argument('--DNN_OPTIMIZER_LR', type=float, default= 0.1)
    parser.add_argument('--DNN_L1_REG', type=float, default=0.0)  # Regularization rate for FtrlOptimizer
    parser.add_argument('--DNN_L2_REG', type=float, default=0.0)
    parser.add_argument('--DNN_MOMENTUM', type=float, default=0.0)  # Momentum for MomentumOptimizer or RMSPropOptimizer
    # Layer dimensions. Defined as follows to make this notebook runnable from Hyperparameter tuning services like AzureML Hyperdrive
    parser.add_argument('--DNN_HIDDEN_LAYER_1', type=int, default=0)  # Set 0 to not use this layer
    parser.add_argument('--DNN_HIDDEN_LAYER_2', type=int, default=64)  # Set 0 to not use this layer
    parser.add_argument('--DNN_HIDDEN_LAYER_3', type=int, default=128)  # Set 0 to not use this layer
    parser.add_argument('--DNN_HIDDEN_LAYER_4', type=int, default=512)  # Note, at least one layer should have nodes.
    parser.add_argument('--DNN_USER_DIM', type=int, default=32)  # User embedding feature dimension
    parser.add_argument('--DNN_ITEM_DIM', type=int, default=16)  # Item embedding feature dimension
    parser.add_argument('--DNN_DROPOUT', type=float, default=0.8)
    parser.add_argument('--DNN_BATCH_NORM', type=int, default=1)  # 1 to use batch normalization, 0 if not.

    # Item feature information
    parser.add_argument('--ITEM_FEAT_COL', type=str, default='features')
    parser.add_argument('--categorical_feats', type=str, default="")
    parser.add_argument('--continuous_feats', type=str, default="")
    input_args = parser.parse_args()
    return vars(input_args)

# def get_top_k(dataframe, k):
#     user_unique_set = set(dataframe['userID'])
#     return_dataframe = pd.DataFrame()
#     for i in user_unique_set:
#         dataframe_by_user = dataframe.loc[dataframe['userID'] == i]
#         dataframe_by_user = dataframe_by_user.sort_values(by='prediction', ascending=False)[:k]
#         return_dataframe = return_dataframe.append(dataframe_by_user)
#     return return_dataframe

def load_item_features(config, data_path):
    item_feature_file = single_xpath(
        config.get_xml(), '/librec-auto/features/item-feature-file').text
    item_feature_path = data_path / item_feature_file

    if not item_feature_path.exists():
        print("Cannot locate item features. Path: " + item_feature_path)
        return None

    item_feature_df = pd.read_csv(item_feature_path,
                                      names=['item_id', 'feature', 'value'])
    return item_feature_df

def main():
    args = read_args()
    # global params for both models:
    model_type = args['model_type']
    batch_size = args['BATCH_SIZE']
    training_path = args['train']
    test_path = args['test']
    result_file_path = Path(args['result'])

    #params for SVAE model:
    top_k = args['max_len']
    latent_dim = args['LATENT_DIM']
    encoder_dims = []
    encoder_dims.append(args['ENCODER_DIMS'])
    intermediate_dim = args['INTERMEDIATE_DIM']
    num_epochs = args['NUM_EPOCHS']
    holdout_pct = args['HOLDOUT_PCT']
    thresh = args['BINARIZATION_THRESHOLD']
    temp_weights_path = result_file_path.parent / 'svae_weights.hdf5'

    #params for only wide and deep code:
    eval_while_training = args['EVAL_WHILE_TRAINING']
    model_dir = Path(args['model'])
    item_feat_col = args['ITEM_FEAT_COL']
    # RANDOM_SEED = SEED  # Set seed for deterministic result
    steps = args['STEPS']
    linear_optimizer = args['LINEAR_OPTIMIZER']
    linear_optimizer_lr = args['LINEAR_OPTIMIZER_LR']
    linear_l1_reg = args['LINEAR_L1_REG']
    linear_l2_reg = args['LINEAR_L2_REG']
    linear_momentum = args['LINEAR_MOMENTUM']
    # -- Hyperparams for DNN model --
    dnn_optimizer = args['DNN_OPTIMIZER']
    dnn_optimizer_lr = args['DNN_OPTIMIZER_LR']
    dnn_l1_reg = args['DNN_L1_REG']  # Regularization rate for FtrlOptimizer
    dnn_l2_reg = args['DNN_L2_REG']
    dnn_momentum = args['DNN_MOMENTUM']  # Momentum for MomentumOptimizer or RMSPropOptimizer
    # Layer dimensions. Defined as follows to make this notebook runnable from Hyperparameter tuning services like AzureML Hyperdrive
    dnn_hidden_layer1 = args['DNN_HIDDEN_LAYER_1']  # Set 0 to not use this layer
    dnn_hidden_layer2 = args['DNN_HIDDEN_LAYER_2']  # Set 0 to not use this layer
    dnn_hidden_layer3 = args['DNN_HIDDEN_LAYER_3']  # Set 0 to not use this layer
    dnn_hidden_layer4 = args['DNN_HIDDEN_LAYER_4']  # Note, at least one layer should have nodes.
    DNN_HIDDEN_UNITS = [h for h in [dnn_hidden_layer1, dnn_hidden_layer2, dnn_hidden_layer3, dnn_hidden_layer4] if
                        h > 0]
    dnn_user_dim = args['DNN_USER_DIM']  # User embedding feature dimension
    dnn_item_dim = args['DNN_ITEM_DIM']  # Item embedding feature dimension
    dnn_dropout = args['DNN_DROPOUT']
    dnn_batch_norm = args['DNN_BATCH_NORM']  # 1 to use batch normalization, 0 if not.
    # Metrics to use for evaluation of wide and deep model
    RANKING_METRICS = [
        evaluator.ndcg_at_k.__name__,
        evaluator.precision_at_k.__name__,
    ]
    RATING_METRICS = [
        evaluator.rmse.__name__,
        evaluator.mae.__name__,
    ]
    # Use session hook to evaluate model while training
    EVALUATE_WHILE_TRAINING = True
    if len(args['categorical_feats']) > 0:
        categorical_feats = args['categorical_feats'].split(",")
    else:
        categorical_feats = []
    if len(args['continuous_feats']) > 0:
        continuous_feats = args['continuous_feats'].split(",")
    else:
        continuous_feats = []
    if model_type == 'wide_deep':
        #Code from MS RecSys here
        print("***** Running MS Recommendation Code Now ******")
        ratings_data = pd.read_csv(training_path,
                               sep="	", header=None)
        ratings_data.columns = ["user_id", "item_id", "rating"]
        config = read_config_file(args['conf'], '.')
        data_dir = single_xpath(config.get_xml(), '/librec-auto/data/data-dir').text
        data_path = Path(data_dir)
        data_path = data_path.resolve()
        item_data = load_item_features(config, data_path)
        print("\nSuccessfully loaded item features")
        item_data_expanded = item_data.pivot_table(index=['item_id'], columns='feature', values='value').reset_index()
        item_data_expanded.rename_axis(None, axis=1, inplace=True)

        # Code to generalize the correct dataset creation with categorical & continuous variables
        # The following creates a large pandas dataframe with one hot encoding of all features
        # TODO: Fix this to use the tensorflow Record to feed data in sequentially when features have high cardinality
        if len(categorical_feats) > 0 and len(continuous_feats) > 0:
            categorical_dfs = [item_data_expanded[["item_id"] + continuous_feats]]
            for feat in categorical_feats:
                categorical_dfs.append(pd.get_dummies(item_data_expanded[feat], prefix=feat))
            concatenated_dataframes = pd.concat(categorical_dfs, axis=1)
        elif len(categorical_feats) > 0:
            categorical_dfs = [item_data_expanded[["item_id"]]]
            for feat in categorical_feats:
                categorical_dfs.append(pd.get_dummies(item_data_expanded[feat], prefix=feat))
            concatenated_dataframes = pd.concat(categorical_dfs, axis=1)
        else:
            concatenated_dataframes = item_data_expanded[["item_id"] + continuous_feats]

        # merge both datasets (ratings and concatenated item features)
        # to get a user, item, rating, featureslist dataframe
        features_lists = []
        for index, row in concatenated_dataframes.iterrows():
            features_list = []
            i = 0
            for column_name in concatenated_dataframes.columns:
                features_list.append(row[column_name])
                i += 1
            features_lists.append(features_list[1:])

        item_data_expanded['features'] = features_lists
        data = pd.merge(ratings_data[['user_id', 'item_id', 'rating']], item_data_expanded[['item_id', 'features']],
                        on="item_id")
        data.columns = ['userID', 'itemID', 'rating', 'features']

        #DELETE ALL OF THIS IF YOU GET IT RUNNING
        # # merge both datasets to get a user, item, rating, featureslist dataframe
        # features_lists = []
        # for index, row in item_data_expanded.iterrows():
        #     features_list = []
        #     features_list.append(row['author_id'])
        #     features_list.append(row['item_city'])
        #     features_list.append(row['channel'])
        #     features_list.append(row['music_id'])
        #     features_list.append(row['video_duration'])
        #     features_list.append(row['gender'])
        #     features_list.append(row['beauty'])
        #     features_lists.append(features_list)
        #
        # item_data_expanded['features'] = features_lists
        # data = pd.merge(ratings_data[['user_id', 'item_id', 'rating']], item_data_expanded[['item_id', 'features']],
        #                 on="item_id")
        # data.columns = ['userID', 'itemID', 'rating', 'features']
        print("*** SUCCESSFULLY CREATED THE DATASET FOR THIS MODEL***")
        train, test = python_random_split(data, ratio=0.75, seed=SEED)
        print("{} train samples and {} test samples".format(len(train), len(test)))
        # Unique items in the dataset
        if item_feat_col is None:
            items = data.drop_duplicates(ITEM_COL)[[ITEM_COL]].reset_index(drop=True)
            item_feat_shape = None
        else:
            items = data.drop_duplicates(ITEM_COL)[[ITEM_COL, item_feat_col]].reset_index(drop=True)
            item_feat_shape = len(items[item_feat_col][0])
        # Unique users in the dataset
        users = data.drop_duplicates(USER_COL)[[USER_COL]].reset_index(drop=True)

        print("Total {} items and {} users in the dataset".format(len(items), len(users)))
        # Make temporary model directory to store model (deletes after code is run)
        if model_dir is None:
            TMP_DIR = TemporaryDirectory()
            model_dir = TMP_DIR.name
        else:
            if os.path.exists(model_dir) and os.listdir(model_dir):
                raise ValueError(
                    "Model exists in {}. Use different directory name or "
                    "remove the existing checkpoint files first".format(model_dir)
                )
            TMP_DIR = None
            temp_model_dir = model_dir
        # Create model checkpoint every n steps. We store the model 5 times.
        save_checkpoints_steps = max(1, steps // 5)
        # Define wide (linear) and deep (dnn) features
        wide_columns, deep_columns = wide_deep.build_feature_columns(
            users=users[USER_COL].values,
            items=items[ITEM_COL].values,
            user_col=USER_COL,
            item_col=ITEM_COL,
            item_feat_col=item_feat_col,
            crossed_feat_dim=1000,
            user_dim=dnn_user_dim,
            item_dim=dnn_item_dim,
            item_feat_shape=item_feat_shape,
            model_type=model_type,
        )

        print("Wide feature specs:")
        for c in wide_columns:
            print("\t", str(c)[:100], "...")
        print("Deep feature specs:")
        for c in deep_columns:
            print("\t", str(c)[:100], "...")

        # Build a model based on the parameters
        model = wide_deep.build_model(
            model_dir=temp_model_dir,
            wide_columns=wide_columns,
            deep_columns=deep_columns,
            linear_optimizer=tf_utils.build_optimizer(linear_optimizer, linear_optimizer_lr, **{
                'l1_regularization_strength': linear_l1_reg,
                'l2_regularization_strength': linear_l2_reg,
                'momentum': linear_momentum,
            }),
            dnn_optimizer=tf_utils.build_optimizer(dnn_optimizer, dnn_optimizer_lr, **{
                'l1_regularization_strength': dnn_l1_reg,
                'l2_regularization_strength': dnn_l2_reg,
                'momentum': dnn_momentum,
            }),
            dnn_hidden_units=DNN_HIDDEN_UNITS,
            dnn_dropout=dnn_dropout,
            dnn_batch_norm=(dnn_batch_norm == 1),
            log_every_n_iter=max(1, steps // 10),  # log 10 times
            save_checkpoints_steps=save_checkpoints_steps,
            seed=SEED
        )
        cols = {
            'col_user': USER_COL,
            'col_item': ITEM_COL,
            'col_rating': RATING_COL,
            'col_prediction': PREDICT_COL,
        }

        # Prepare ranking evaluation set, i.e. get the cross join of all user-item pairs
        ranking_pool = user_item_pairs(
            user_df=users,
            item_df=items,
            user_col=USER_COL,
            item_col=ITEM_COL,
            user_item_filter_df=train,  # Remove seen items
            shuffle=True,
            seed=SEED
        )

        # Define training hooks to track performance while training
        hooks = []
        if EVALUATE_WHILE_TRAINING:
            evaluation_logger = tf_utils.MetricsLogger()
            for metrics in (RANKING_METRICS, RATING_METRICS):
                if len(metrics) > 0:
                    hooks.append(
                        tf_utils.evaluation_log_hook(
                            model,
                            logger=evaluation_logger,
                            true_df=test,
                            y_col=RATING_COL,
                            eval_df=ranking_pool if metrics == RANKING_METRICS else test.drop(RATING_COL, axis=1),
                            every_n_iter=save_checkpoints_steps,
                            model_dir=temp_model_dir,
                            eval_fns=[evaluator.metrics[m] for m in metrics],
                            **({**cols, 'k': top_k} if metrics == RANKING_METRICS else cols)
                        )
                    )

        # Define training input (sample feeding) function
        train_fn = tf_utils.pandas_input_fn(
            df=train,
            y_col=RATING_COL,
            batch_size=batch_size,
            num_epochs=None,  # We use steps=TRAIN_STEPS instead.
            shuffle=True,
            seed=SEED,
        )

        print("\n*** TRAINING THE MODEL **", end='\n')

        print(
            "Training steps = {}, Batch size = {} (num epochs = {})"
                .format(steps, batch_size, (steps * batch_size) // len(train))
        )
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)

        try:
            model.train(
                input_fn=train_fn,
                hooks=hooks,
                steps=steps
            )
        except tf.train.NanLossDuringTrainingError:
            import warnings
            warnings.warn(
                "Training stopped with NanLossDuringTrainingError. "
                "Try other optimizers, smaller batch size and/or smaller learning rate."
            )
        print("\n*****End of Training", end='\n')
        if len(RATING_METRICS) > 0:
            predictions = list(model.predict(input_fn=tf_utils.pandas_input_fn(df=test)))
            prediction_df = test.drop(RATING_COL, axis=1)
            prediction_df[PREDICT_COL] = [p['predictions'][0] for p in predictions]

            rating_results = {}
            for m in RATING_METRICS:
                result = evaluator.metrics[m](test, prediction_df, **cols)
                sb.glue(m, result)
                rating_results[m] = result
            print("**RATING RESULTS: ", rating_results)

        if len(RANKING_METRICS) > 0:
            predictions = list(model.predict(input_fn=tf_utils.pandas_input_fn(df=ranking_pool)))
            prediction_df = ranking_pool.copy()
            prediction_df[PREDICT_COL] = [p['predictions'][0] for p in predictions]

            ranking_results = {}
            for m in RANKING_METRICS:
                result = evaluator.metrics[m](test, prediction_df, **{**cols, 'k': top_k})
                sb.glue(m, result)
                ranking_results[m] = result
            print("**RANKING METRICS: ", ranking_results)

        top_k_df = prediction_df[['userID', 'itemID', PREDICT_COL]]
        top_k_df.columns = ['userID', 'itemID', 'rating']
        top_k_sorted = top_k_df.sort_values(by=['userID', 'rating'], ascending=[True, False])
        top_k_sorted.to_csv(result_file_path, header=None, index=None, sep=',')

        print("*** FINISHED!")
        # os.makedirs(EXPORT_DIR_BASE, exist_ok=True)



    elif model_type == 'StandardVAE':
        #MIGHT NEED TO COMMENT OUT THE FOLLOWING LINE! important
        # tensorflow.python.framework_ops.disable_eager_execution()
        train_df = pd.read_csv(training_path,
                            sep="	", header=None)
        train_df.columns = ["userID", "itemID", "rating"]
        unique_train_items = pd.unique(train_df['itemID'])
        # Create train/validation/test users

        unique_users = sorted(train_df.userID.unique())
        np.random.seed(SEED)
        unique_users = np.random.permutation(unique_users)

        n_users = len(unique_users)
        heldout_users = int((n_users * holdout_pct) / 100)

        train_users = unique_users[:(n_users - heldout_users)]

        val_users = unique_users[(n_users - heldout_users):]

        # For training set keep only users that are in train_users list
        train_set = train_df.loc[train_df['userID'].isin(train_users)]

        # For validation set keep only users that are in val_users list
        val_set = train_df.loc[train_df['userID'].isin(val_users)]

        # For validation set keep only movies that used in training set
        val_set = val_set.loc[val_set['itemID'].isin(unique_train_items)]

        # Theoretically we could use this for predicting rating values
        # Right now will only work for list-wise predictions
        if top_k <= 0:
            test = pd.read_csv(test_path,
                               sep="	", header=None)
            test.columns = ["userID", "itemID", "rating"]

        am_train = AffinityMatrix(df=train_set, items_list=unique_train_items)
        am_val = AffinityMatrix(df=val_set, items_list=unique_train_items)

        train_set, _, _ = am_train.gen_affinity_matrix()
        val_data, val_map_users, val_map_items = am_val.gen_affinity_matrix()
        val_data_tr, val_data_te = numpy_stratified_split(val_data, ratio=0.75, seed=SEED)
        # Binarize validation data: training part
        train_data = binarize(a=train_set, threshold=thresh)
        val_data = binarize(a=val_data, threshold=thresh)
        val_data_tr = binarize(a=val_data_tr, threshold=thresh)

        # Binarize validation data: testing part (save non-binary version in the separate object, will be used for calculating NDCG)
        val_data_te_ratings = val_data_te.copy()
        val_data_te = binarize(a=val_data_te, threshold=3.5)

        print('Number of users: {}'.format(train_set.shape[0]))
        print('Number of items: {}'.format(train_set.shape[1]))

        #train model
        # svae = StandardVAE(
        #     k=latent_dim,
        #     encoder_structure=encoder_dims,
        #     act_fn=act_func,
        #     likelihood=likelihood,
        #     n_epochs=num_epochs,
        #     batch_size=batch_size,
        #     learning_rate=learning_rate,
        #     seed=SEED,
        #     use_gpu=torch.cuda.is_available(),
        #     verbose=True
        # )

        svae = StandardVAE(n_users=train_set.shape[0],  # Number of unique users in the training set
                    original_dim=train_set.shape[1],  # Number of unique items in the training set
                    intermediate_dim=intermediate_dim,
                    latent_dim=latent_dim,
                    n_epochs=num_epochs,
                    batch_size=batch_size,
                    k=top_k,
                    verbose=0,
                    seed=SEED,
                    save_path=str(temp_weights_path),
                    drop_encoder=0.5,
                    drop_decoder=0.5,
                    annealing=False,
                    beta=1.0
                    )

        svae.fit(x_train=train_data,
                                 x_valid=val_data,
                                 x_val_tr=val_data_tr,
                                 x_val_te=val_data_te_ratings, # with the original ratings
                                 mapper=am_val
                                 )

        # Might be able to use recommend_k_items instead?
        final_result = svae.recommend_k_items(train_data, top_k, remove_seen=True)
        #all_predictions = predict_ranking(svae, train, usercol='userID', itemcol='itemID', remove_seen=True)
        #final_result = get_top_k(all_predictions, top_k)
        top_k_df = am_train.map_back_sparse(final_result, kind='prediction')
        top_k_df.columns = ['userID', 'itemID', 'rating']

        top_k_sorted = top_k_df.sort_values(by=['userID', 'rating'], ascending=[True, False])

        top_k_sorted.to_csv(result_file_path, header=None, index=None, sep=',')

if __name__ == '__main__':
    main()
