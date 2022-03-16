from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core import ConfigCmd
from librec_auto.core.util import Status
import optuna

class TellCmd(Cmd):
    def __init__(self, args, config, current_exp_no, study, trial, metric, direction):
        print("inside tell")
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

            if i != self.current_exp_no:
                i += 1
                continue
            status = Status(sub_paths)
            store_val = status.get_metric_info(status._log, BBO = True)[self.title_map[self.metric]]
            break
                
        return float(store_val)
        
    def run_experiments(self):
        # params = self.space
        # if self.current_exp_no != 0:
        #     self.modify_xml(params)
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

    