from librec_auto.core.util import Status
from librec_auto.core.util.errors import *
import optuna


# Borrowed from https://stackoverflow.com/questions/58820574/how-to-sample-parameters-without-duplicates-in-optuna
# Prevents repeated parameter values in the sampling. It seems like this should be the default
# behavior.
class RepeatPruner(optuna.pruners.BasePruner):
    def prune(self, study, trial):
        # type: (Study, FrozenTrial) -> bool

        trials = study.get_trials(deepcopy=False)
        completed_trials = [t.params for t in trials if t.state == optuna.trial.TrialState.COMPLETE]
        n_trials = len(completed_trials)

        if n_trials == 0:
            return False

        if trial.params in completed_trials:
            return True

        return False


#module to optimize
class BBO:
    '''
    Class for managing optuna optimization.
    '''
    
    def __init__(self, Ranges, num_of_vars, command, config, ranges = None, file_path = None):
        
        self.Ranges = Ranges
        self.num_of_vars = num_of_vars
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
        self.command = command
        self.index = 0
        self.current_command = self.command[self.index]
        self.config = config
        self.file_path = file_path
        self.create_params = True
        self.metric_map = {'auc': 'positive', 'ap': 'positive','arhr': 'positive',
                'diversity': 'positive', 'hitrate': 'positive','idcg': 'positive',
                'ndcg': 'positive', 'precision': 'positive', 'recall': 'positive',
                'rr': 'positive', 'featurediversity': 'positive', 'novelty': 'positive',
                'entropy': 'positive','icov': 'positive', 'dppf': 'positive', 'dpcf': 'positive',
                'giniindex': 'negative', 'mae': 'negative','mpe': 'negative','mse': 'negative','rmse': 'negative',
                'csp': 'negative', 'psp': 'negative','miscalib': 'negative','nonpar': 'negative','valunfairness': 'negative',
                'absunfairness': 'negative','overestimate': 'negative','underestimate': 'negative','ppr': 'negative'        
                }
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

        if ranges == []:
            self.discrete = None
        else:
            self.discrete = ranges

    #creates hyperparameter dictionary in optuna format
    # Might need to move into compile.py or create an object    
    def create_space(self, trial):
        # self.space = {self.alphabet[i]: hp.hp.uniform(self.alphabet[i], self.Ranges[i][0], self.Ranges[i][1]) for i in range(self.num_of_vars)}
        if self.discrete == None:
            self.space = {self.alphabet[i]: trial.suggest_float(self.alphabet[i],self.Ranges[i][0], self.Ranges[i][1]) for i in range(self.num_of_vars)}
        else:
            self.space = {}
            for i,type in enumerate(self.discrete):
                if type == "continuous":
                    self.space[self.alphabet[i]] = trial.suggest_float(self.alphabet[i],self.Ranges[i][0], self.Ranges[i][1])
                else:
                    self.space[self.alphabet[i]] = trial.suggest_int(self.alphabet[i],self.Ranges[i][0], self.Ranges[i][1])
    #uses direction from existing metrics or user chosen direction if custom
    def set_optimization_direction(self, metric):
        self.metric = metric
        if metric == "higher":
            self.direction = "positive"
        elif metric == "lower":
            self.direction = "negative"
        else:
            if metric not in self.metric_map:
                raise InvalidConfiguration("Optimization", 
                "You must specify whether your metric should be optimized in the positive or negative direction")

            self.direction = self.metric_map[metric]
    
    #Uses status object in order to get data from most recent iteration
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
    
    #All function required for experiments are called from here
    def run_experiments(self, trial):

        if self.create_params is not False:
            self.create_space(trial)
            # self.create_params = False

        params = self.space
        if self.exp_no != 0:
            self.modify_xml(params)

        self.current_command.execute(self.config)
        data = self.get_data()
        self.exp_no += 1
        
        if self.exp_no != self.total_exp_no:
            self.change_current_command()

        return data
    
    #sends values to write configs to create next experiment
    def modify_xml(self, params):
        self.config.write_exp_configs(val = list(params.values()), iteration = self.exp_no)
        
    # changes which command needs to be run    
    def change_current_command(self):
        self.index += 1
        self.current_command = self.command[self.index]

    #purge is run at the beginning, must be handled seperatly from remaining steps
    def run_purge(self, command):
        command.execute(self.config)
        return command._files._study_path
        
    def run(self,total_exp_no):
        # self.store_params = self.space
        self.exp_no = 0
        self.total_exp_no = total_exp_no
        self.config.get_sub_exp_count()
        # best = fmin(fn=self.run_experiments, space = self.store_params, algo=tpe.suggest, max_evals=total_exp_no)
        study = optuna.create_study(pruner=RepeatPruner())

        if self.direction == 'positive':
            study = optuna.create_study(direction = "maximize", pruner=RepeatPruner())
        
        for i in range(total_exp_no):
            trial = study.ask()

            self.create_space(trial)

            result = self.run_experiments(trial)

            study.tell(trial,result)


        print("Best Trial:")

        trial = study.best_trial

        print("Value:", trial.value)

        print("Params: ")

        for key, value in trial.params.items():
            print("{}:{}".format(key,value))