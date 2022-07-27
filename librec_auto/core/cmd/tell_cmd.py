from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core import ConfigCmd
from librec_auto.core.util import Status, StudyStatus
import optuna

class TellCmd(Cmd):
    def __init__(self, args, config, current_exp_no, study, trial, metric, direction, old_librec_value_command = None, new_val = None, hack = False):
        # print("inside tell")
        self.config = config
        self.args = args
        self.current_exp_no = current_exp_no
        self.study = study
        self.trial = trial
        self.metric = metric
        self.direction = direction
        self.status = 3 
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

        self.hack = hack

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

            # if i != self.current_exp_no:
            #     i += 1
            #     continue
            # status = Status(sub_paths)
            study_status = StudyStatus(self.config)
            if self.hack is not False:
                print("hack = true")
                old_val = self.old_librec_value_command._previous_status["ndcg_metric.py"]
                store_dict = self.new_val._previous_status["ndcg_metric.py"]
                print(store_dict, old_val)
                store_val = max(0,(store_dict - 0.9*old_val)) + self.new_val._previous_status["psp.py"]

                s = str(self.config._files.get_exp_paths(self.current_exp_no)._path_dict["output"])[:-10] + "output_combo.txt"
                with open(s,"w+") as f:
                    f.write(str(store_val))
            else:
                if self.metric in self.title_map:
                    store_val = study_status.get_metric_averages(self.metric)[self.title_map[self.metric]]
                else:
                    print(study_status._experiments.values())
                    store_val = study_status.get_metric_averages(self.metric)[0]
                print("STORE VAL",store_val)
            break
                
        return float(store_val)
        
    def run_experiments(self):
        data = self.get_data()
        return data
    
    def execute(self, command):
        print("running tell")
        data = self.run_experiments()
        pruned_trial = False
        if self.trial.should_prune():
            pruned_trial = True

        if pruned_trial:
            self.study.tell(self.trial, state=optuna.trial.TrialState.PRUNED)
        else:
            self.study.tell(self.trial, self.run_experiments())

    