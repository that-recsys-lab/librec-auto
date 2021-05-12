import numpy as np
import math

from .list_based_metric import ListBasedMetric


class NdcgMetric(ListBasedMetric):
    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array) -> None:
        super().__init__(params, test_data, result_data)
        self._name = 'NDCG'

    def evaluate_user(self, test_user_data: np.array,
                      result_user_data: np.array) -> float:
        rec_num = int(self._params['list-size'])

        # modified from https://github.com/nasimsonboli/OFAiR/blob/main/source%20code/OFAiR_Evaluation.ipynb
        idealOrder = test_user_data
        idealDCG = 0.0

        for j in range(min(rec_num, len(idealOrder))):
            idealDCG += ((math.pow(2.0,
                                   len(idealOrder) - j) - 1) /
                         math.log(2.0 + j))

        recDCG = 0.0
        test_user_items = list(test_user_data[:, 1])

        for j in range(rec_num):
            item = int(result_user_data[j][1])
            if item in test_user_items:
                rank = len(test_user_items) - test_user_items.index(
                    item)  # why ground truth?
                recDCG += ((math.pow(2.0, rank) - 1) / math.log(1.0 + j + 1))
        return (recDCG / idealDCG)

    def postprocessing(self):
        return np.average(self._values)
