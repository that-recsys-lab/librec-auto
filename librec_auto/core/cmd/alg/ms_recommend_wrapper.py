#Name: Zijun Liu
#File: Deep Learning Recommendation Algorithm
#CIKM 2021

import argparse
import pandas as pd
import numpy as np
import tensorflow
from pathlib import Path

# from recommenders.reco_utils.recommender.cornac.cornac_utils import predict_ranking
from recommenders.utils.constants import SEED
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
    parser.add_argument('--model', choices=['StandardVAE'],
                        default='StandardVAE')
    parser.add_argument('--max_len', type=int, default=10)
    parser.add_argument('--LATENT_DIM', type=int, default=50)
    parser.add_argument('--ENCODER_DIMS', type=int, default=100)
    parser.add_argument('--INTERMEDIATE_DIM', type=str, default=200)
    parser.add_argument('--NUM_EPOCHS', type=int, default=500)
    parser.add_argument('--BATCH_SIZE', type=int, default=128)
    parser.add_argument('--HOLDOUT_PCT', type=int, default=10)
    parser.add_argument('--BINARIZATION_THRESHOLD', type=float, default=3.5)

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

def main():
    args = read_args()
    model = args['model']
    top_k = args['max_len']
    latent_dim = args['LATENT_DIM']
    encoder_dims = []
    encoder_dims.append(args['ENCODER_DIMS'])
    intermediate_dim = args['INTERMEDIATE_DIM']
    num_epochs = args['NUM_EPOCHS']
    batch_size = args['BATCH_SIZE']
    holdout_pct = args['HOLDOUT_PCT']
    thresh = args['BINARIZATION_THRESHOLD']

    training_path = args['train']
    test_path = args['test']
    result_file_path = Path(args['result'])
    temp_weights_path = result_file_path.parent / 'svae_weights.hdf5'

    if model == 'StandardVAE':
        tensorflow.python.framework_ops.disable_eager_execution()
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
