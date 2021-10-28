#Put this in its own file: amortized_attention_metric.py

from librec_auto.core.eval.metrics.list_based_metric import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd
import sklearn
from sklearn.preprocessing import minmax_scale
import numpy as np
import math
import argparse
import numpy.random as random

def read_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Amortized Attention')
    parser.add_argument('--conf', help='Path to config file')
    parser.add_argument('--test', help='Path to test.')
    parser.add_argument('--result', help='Path to results.')
    parser.add_argument('--output-file', help='The output pickle file.')

    # Custom params defined in the config go here
    parser.add_argument('--amortized_attention', help='PUT A DESCRIPTION HERE')
    parser.add_argument('--list_size', help='Size of the list for NDCG.')

    input_args = parser.parse_args()
    return vars(input_args)


class CustomAmortizedAttentionMetric(ListBasedMetric):
    def __init__(self, params: dict, conf:ConfigCmd, test_data: np.array,
             result_data: np.array, output_file) -> None:
        super().__init__(params, conf, test_data, result_data, output_file)
        self._name = 'amortized_attention'

    #this was implemented for individual fairness
    #as explained in the paper: https://arxiv.org/pdf/1805.01788.pdf
    def evaluate_user(self, test_user_data: np.array,
                  result_user_data: np.array) -> float:
        rec_num = int(self._params['list_size'])
        predicted_results = self._result_data
        list_size = rec_num
        # calculating the normalized attention of items in all lists for a user
        # attention from being 1st in the list is 1
        # attention from being last in the list is 0
        # attention from being in another place in the list is proportional to that place in the list
        scores = np.array(range(list_size, 0, -1))
        norm_attention_per_list = minmax_scale(scores, feature_range=(0, 1))
        # calculating the normalized rating predictions to scale them from 0 to 1 for all u,i,r in the result data
        norm_rating_predictions = minmax_scale(predicted_results[:, 2], feature_range=(0, 1))
        # total unfairness starts at 0 (which is equal to 100% fairness)
        total_unfairness = 0
        # start by setting the list-wise attention and relevance values to zero
        attention_this_list = 0
        relevance_this_list = 0
        # loop through each item's predicted rating
        for i in range(len(predicted_results)):
            # get which index in the list we are currently in
            list_index = i % list_size
            # reset the attention and relevance values each time we hit a new user (a new list)
            # add the attention that this item gets to this lists' total attention
            attention_this_list += norm_attention_per_list[list_index]
            # add the relevance this item has to this lists' total relevance
            relevance_this_list += norm_rating_predictions[i]
            # once we reach the end of the list, comput the unfairness of this list and add it to the total unfairness
            if list_index == list_size - 1:
                unfairness_this_list = abs(attention_this_list - relevance_this_list)
                total_unfairness += unfairness_this_list
                attention_this_list = 0
                relevance_this_list = 0
        # return the total_unfairness value
        # zero == perfect fairness, further from zero implies more unfairness
        return total_unfairness

    def postprocessing(self):
        return np.average(self._values)
    
if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], '.')
    params = {'list_size': args['list_size']}

    test_data = ListBasedMetric.read_data_from_file(
        args['test']
    )
    result_data = ListBasedMetric.read_data_from_file(
        args['result'],
        delimiter=','
    )
    print("****Creating Amortized Attention Metric/n")
    custom = CustomAmortizedAttentionMetric(params, config, test_data, result_data,
                            args['output_file'])
    print('****EVALUATING Amortized Attention Metric/n')
    custom.evaluate()