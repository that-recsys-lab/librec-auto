from collections import OrderedDict, defaultdict
from librec_auto.core.util import Files, utils, build_parent_path, LibrecProperties, \
    xml_load_from_path, Library, LibraryColl, merge_elements, VarColl, Status
from librec_auto.core.util.xml_utils import single_xpath
from lxml import etree
import copy
import logging
from pathlib import Path
from librec_auto.core.config_lib import ConfigLibCollection, ConfigLib
import re
import hyperopt as hp
from hyperopt import fmin, tpe, STATUS_OK
import os

class BBO:
    
    def __init__(self, Ranges, num_of_vars, command, config, file_path = None):
        
        self.Ranges = Ranges
        self.num_of_vars = num_of_vars
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
        self.command = command
        self.index = 0
        self.current_command = self.command[self.index]
        self.config = config
        self.file_path = file_path
        self.metric_map = {'auc': 'positive', 'ap': 'positive','arhr': 'positive','diversity': 'positive', 'hitrate': 'positive','idcg': 'positive','ndcg': 'positive', 'precision': 'positive', 'recall': 'positive', 'rr': 'positive', 'featurediversity': 'positive', 'novelty': 'positive', 'entropy': 'positive', \
                'icov': 'positive', 'dppf': 'positive', 'dpcf': 'positive', \
                'giniindex': 'negative', 'mae': 'negative','mpe': 'negative','mse': 'negative','rmse': 'negative', \
                'csp': 'negative', 'psp': 'negative','miscalib': 'negative','nonpar': 'negative','valunfairness': 'negative', \
                'absunfairness': 'negative','overestimate': 'negative','underestimate': 'negative','ppr': 'negative'        
                }
        self.title_map = {'auc': 'AUCEvaluator', 'ap': 'AveragePrecisionEvaluator','arhr': 'AverageReciprocalHitRankEvaluator','diversity': 'DiversityEvaluator', 'hitrate': 'HitRateEvaluator','idcg': 'IdealDCGEvaluator','ndcg': 'NormalizedDCGEvaluator', 'precision': 'PrecisionEvaluator', 'recall': 'RecallEvaluator', 'rr': 'ReciprocalRankEvaluator', 'featurediversity': 'DiversityByFeaturesEvaluator', 'novelty': 'NoveltyEvaluator', 'entropy': 'EntropyEvaluator', \
                'icov': 'ItemCoverageEvaluator', 'dppf': 'DiscountedProportionalPFairnessEvaluator', 'dpcf': 'DiscountedProportionalCFairnessEvaluator', \
                'giniindex': 'GiniIndexEvaluator', 'mae': 'MAEEvaluator','mpe': 'MPEEvaluator','mse': 'MSEEvaluator','rmse': 'RMSEEvaluator', \
                'csp': 'CStatisticalParityEvaluator', 'psp': 'PStatisticalParityEvaluator','miscalib': 'MiscalibrationEvaluator','nonpar': 'NonParityUnfairnessEvaluator','valunfairness': 'ValueUnfairnessEvaluator', \
                'absunfairness': 'AbsoluteUnfairnessEvaluator','overestimate': 'OverestimationUnfairnessEvaluator','underestimate': 'UnderestimationUnfairnessEvaluator','ppr': 'PPercentRuleEvaluator'        
                }
        
    def create_space(self):
        self.space = {self.alphabet[i]: hp.hp.uniform(self.alphabet[i], self.Ranges[i][0], self.Ranges[i][1]) for i in range(self.num_of_vars)}

    def set_optimization_direction(self, metric):
        self.metric = metric

        if metric == "higher":
            self.direction = "positive"
        elif metric == "lower":
            self.direction = "negative"
        else:
            if metric not in self.metric_map:
                raise Exception("You must specify whether your metric should be optimized in the positive or negative direction")

            self.direction = self.metric_map[metric]
    
    def get_data(self):
        
        store_val = ''

        i = 0

        for sub_paths in self.config._files.get_exp_paths_iterator():

            if i != self.exp_no:
                i += 1
                continue

            status = Status(sub_paths)
            store_val = status.get_metric_info(status._log, BBO = True)[self.title_map[self.metric]]
            break
                
        return float(store_val)
    
    
    def run_experiments(self,params):
#         self.store_params = [params[self.alphabet[i]] for i in range(len(self.space.keys()))]
        if self.exp_no != 0:
            self.modify_xml(params)
        self.current_command.execute(self.config)
        data = self.get_data()
        self.exp_no += 1
        if self.exp_no != self.total_exp_no:
            self.change_current_command()

        if self.direction == 'positive':
            return {'loss': -data, 'status': STATUS_OK}
        else:
            return {'loss': data, 'status': STATUS_OK}
    
    def modify_xml(self, params):
        self.config.write_exp_configs(BBO = True, val = list(params.values()), iteration = self.exp_no)
        
    def change_current_command(self):
        self.index += 1
        self.current_command = self.command[self.index]

    def run_purge(self, command):
        command.execute(self.config)
        return command._files._study_path
        
    def run(self,total_exp_no):
        self.store_params = self.space
        self.exp_no = 0
        self.total_exp_no = total_exp_no
        # best = fmin(fn=self.run_experiments, space = self.store_params, algo=tpe.suggest, max_evals=total_exp_no)
        best = fmin(fn=self.run_experiments, space = self.store_params, algo=tpe.suggest, max_evals=total_exp_no)