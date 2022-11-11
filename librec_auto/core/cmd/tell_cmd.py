from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core import ConfigCmd
from librec_auto.core.util import Status, StudyStatus
import optuna
import joblib
import numpy as np

class OptimizationFunction():
    def __init__(self, type, new_value, old_value, fairness, acceptable_threshold = 0.9):
        self.type = type
        self.store = {"Additive":self.additive, "Multiplicative":self.multiplicative, "Exponential":self.exponential}
        self.new_value = new_value
        self.old_value = old_value
        self.fairness = fairness
        self.acceptable_threshold = acceptable_threshold

        self.store[type]()

    def additive(self):
        self.value = max(0,(self.new_value - self.acceptable_threshold*float(self.old_value))) + self.fairness

    def multiplicative(self):
        self.value = max(0,(self.new_value - self.acceptable_threshold*float(self.old_value))) * self.fairness

    def exponential(self):
        self.value = max(0,(self.new_value - self.acceptable_threshold*float(self.old_value))) ** self.fairness

class TellCmd(Cmd):
    def __init__(self, args, config, current_exp_no, study, trial, metric, direction, old_librec_value_command = None, new_val = None, optimize_val = None, files = None):
        # print("inside tell")
        self.config = config
        self.args = args
        self.current_exp_no = current_exp_no
        self.study = study
        self.trial = trial
        self.metric = metric
        self.direction = direction
        self.status = 3 
        self.files = files
        self.title_map = {'auc': 'AUCEvaluator', 'ap': 'AveragePrecisionEvaluator','arhr': 'AverageReciprocalHitRankEvaluator','diversity': 'DiversityEvaluator',
        'hitrate': 'HitRateEvaluator','idcg': 'IdealDCGEvaluator','ndcg': 'NormalizedDCGEvaluator',
        'precision': 'PrecisionEvaluator', 'recall': 'RecallEvaluator', 'rr': 'ReciprocalRankEvaluator',
        'featurediversity': 'DiversityByFeaturesEvaluator', 'novelty': 'NoveltyEvaluator', 'entropy': 'EntropyEvaluator',
        'icov': 'ItemCoverageEvaluator', 'dppf': 'DiscountedProportionalPFairnessEvaluator', 'dpcf': 'DiscountedProportionalCFairnessEvaluator',
        'giniindex': 'GiniIndexEvaluator', 'mae': 'MAEEvaluator','mpe': 'MPEEvaluator','mse': 'MSEEvaluator','rmse': 'RMSEEvaluator',
        'csp': 'CStatisticalParityEvaluator', 'psp': 'PStatisticalParityEvaluator','miscalib': 'MiscalibrationEvaluator','nonpar': 'NonParityUnfairnessEvaluator','valunfairness': 'ValueUnfairnessEvaluator',
        'absunfairness'
        : 'AbsoluteUnfairnessEvaluator','overestimate': 'OverestimationUnfairnessEvaluator','underestimate': 'UnderestimationUnfairnessEvaluator','ppr': 'PPercentRuleEvaluator'        
        }

        self.old_librec_value_command = old_librec_value_command

        self.optimize_val = optimize_val

        self.new_val = new_val
        
    def __str__(self):
        return f"TellCmd()"

    def show(self):
        print(str(self))

    def dry_run(self, config):
        print(f'librec-auto (DR): Running Tell command {self}')


    def get_data(self):
        store_val = ''

        i = 0
        for sub_paths in self.config._files.get_exp_paths_iterator():

            study_status = StudyStatus(self.config)
            if self.optimize_val is not None:
                old_val = self.optimize_val

                store_new_val = self.new_val._previous_status["ndcg_metric.py"]
                # store_val = max(0,(store_new_val - 0.95*float(old_val))) + self.new_val._previous_status["psp.py"]
                value_object = OptimizationFunction(store_new_val,old_val, self.new_val._previous_status["psp.py"])
                store_val = value_object.value
                s = str(self.config._files.get_exp_paths(self.current_exp_no)._path_dict["output"])[:-10] + "output_combo.txt"

                with open(s,"w+") as f:
                    f.write(str(store_val))
            else:
                if self.metric in self.title_map:
                    for sub_paths in self.config._files.get_exp_paths_iterator():

                        if i != self.current_exp_no:
                            i += 1
                            continue
                        status = Status(sub_paths)
                        store_val = status.get_metric_info(status._log, BBO = True)[self.title_map[self.metric]]
                        break
                else:
                    print(study_status._experiments.values())
                    for exp in study_status._experiments.values():
                        print(exp._metric_avg)

                    store_val = study_status.get_metric_averages(self.metric)[0]
            break
                
        return float(store_val)
        
    
    def execute(self, command):
        data = self.get_data()
        pruned_trial = False
        if self.trial.should_prune():
            pruned_trial = True

        file_num = str(self.current_exp_no)
        while len(file_num) < 5:
            file_num = "0" + str(file_num)
        path = str(self.files._study_path) + "/exp" + file_num
        joblib.dump(self.study, path+ "/study.pkl")
        if pruned_trial:
            self.study.tell(self.trial, state=optuna.trial.TrialState.PRUNED)
        else:
            self.study.tell(self.trial, data)

    