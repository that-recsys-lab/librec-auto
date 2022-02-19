from librec_auto.core.util.xml_utils import single_xpath
import pandas as pd

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

def get_feature_list(categorical_feats, continuous_feats):
    cat_feats_list = []
    con_feats_list = []
    if len(categorical_feats) > 0:
        cat_feats_list = categorical_feats.split(",")
    if len(continuous_feats) > 0:
        con_feats_list = continuous_feats.split(",")
    return cat_feats_list, con_feats_list

def create_df_wide_deep(ratings_data, item_data, categorical_feats, continuous_feats):
    item_data_expanded = item_data.pivot_table(index=['item_id'], columns='feature', values='value').reset_index()
    item_data_expanded.rename_axis(None, axis=1, inplace=True)

    # Code to generalize the correct dataset creation with categorical & continuous variables
    # The following creates a large pandas dataframe with one hot encoding of all features
    # TODO: Fix this to use the tensorflow Record to feed data in sequentially when features have high cardinality
    # Find more information on TF Record objects here: https://www.tensorflow.org/tutorials/load_data/tfrecord
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
    return data