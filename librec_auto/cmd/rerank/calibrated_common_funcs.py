import pandas as pd
import numpy as np
from multiprocessing import Pool

def KullbackLeiblerDivergence(interactDist, recommendedDist):
    import numpy as np
    alpha = 0.01 # not really a tuning parameter, it's there to make the computation more numerically stable.
    klDive = 0.0
    for i in range(len(interactDist)):
        # By convention, 0 * ln(0/a) = 0, so we can ignore keys in q that aren't in p
        if interactDist[i] == 0.0:
            continue
        # if q = recommendationDist and p = interactedDist, q-hat is the adjusted q.
        # given that KL divergence diverges if recommendationDist or q is zero, we instead use q-hat = (1-alpha).q + alpha . p
        recommendedDist[i] = (1 - alpha) * recommendedDist[i] + alpha * interactDist[i]
        klDive += interactDist[i] * np.log2(interactDist[i] / recommendedDist[i])

    return klDive

#------------------------------------------------------------------------------------------------------------------

def ComputeGenreDistribution(itemList, item_feature_matrix):
    return item_feature_matrix.loc[itemList].sum(axis=0) / len(itemList)

#------------------------------------------------------------------------------------------------------------------

def calibration(userid, item_features, lam, top_k, recoms_df, training_df):

    user_df_rec = recoms_df[recoms_df['userid'] == userid]
    user_df_training = training_df[training_df['userid'] == userid]
    interactDist = ComputeGenreDistribution(user_df_training['itemid'].tolist(), item_features)

    final_list = []
    rerankedList = []
    for k in range(top_k):  # top_k means choose top k items for the final re-ranking.
        all_sc = []
        for i in user_df_rec['itemid'].tolist():

            klDiv = 0
            recommendedDist = ComputeGenreDistribution(rerankedList + [i], item_features)
            klDiv = KullbackLeiblerDivergence(interactDist, recommendedDist)

            t_score = 0
            for j in rerankedList + [i]:
                score = user_df_rec[user_df_rec['itemid'] == j]['score'].values[0]
                t_score += score

            sc = (1 - lam) * score - (lam) * klDiv
            all_sc.append(sc)  # 0.1 0.5 0.2


        sc_asorted = np.argsort(all_sc)[::-1]  # [1, 2, 0]
        top_item = user_df_rec['itemid'].tolist()[sc_asorted[0]]
        top_score = user_df_rec['score'].tolist()[sc_asorted[0]]
        sc_idx = 0
        # if top item already exists in the list, pick the second best item or the third best item

        while top_item in rerankedList:
            if sc_idx in sc_asorted:
                top_item = user_df_rec['itemid'].tolist()[sc_asorted[sc_idx]]
                top_score = user_df_rec['score'].tolist()[sc_asorted[sc_idx]]

                sc_idx += 1

        rerankedList.append(top_item)
        final_list.append([userid, top_item, top_score])

    final_df = pd.DataFrame(final_list, columns=['userid','itemid', 'score'])
    return (final_df)

#------------------------------------------------------------------------------------------------------------------

def getItemFeatureMatrix(fdf):
    item_features_matrix = pd.crosstab(fdf['movieid'], fdf['genre'])
    return item_features_matrix

#------------------------------------------------------------------------------------------------------------------

def execute(recoms_df, tr_df, f_df):

    lam = 0.5 # set it in the config file
    top_k = 10
    result = []
    item_f_mat = getItemFeatureMatrix(f_df)

    # def compute_calibration(u):
    #     return (calibration(u, item_f_mat, lam, top_k, recoms_df, tr_df))
    #
    # pool = Pool(processes=3)
    # userids = recoms_df['userid'].tolist()
    # rerankedList = pool.map(compute_calibration, userids)
    # pool.close()
    # pool.join()

    i = 0
    for userid in list(set(recoms_df['userid'])):
        print('list reranked for user #',i)
        i +=1
        result.append(calibration(userid, item_f_mat, lam, top_k, recoms_df, tr_df))

    rr_df = pd.concat(result)
    return rr_df



