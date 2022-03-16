from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core import ConfigCmd
from librec_auto.core.util import Status
from librec_auto.core.util import Files, create_study_output, BBO, create_log_name, \
    purge_old_logs, InvalidConfiguration, InvalidCommand, UnsupportedFeatureException, \
    LibRecAutoException

class AskCmd(Cmd):
    def __init__(self,Ranges, args, config, current_exp_no, study, ranges, space, num_of_vars, discrete = None):
        # print("init")
        self.config = config
        self.args = args 
        self.current_exp_no = current_exp_no
        self.study = study
        self.status = 3
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
        self.metric_map = {'auc': 'positive', 'ap': 'positive','arhr': 'positive',
                'diversity': 'positive', 'hitrate': 'positive','idcg': 'positive',
                'ndcg': 'positive', 'precision': 'positive', 'recall': 'positive',
                'rr': 'positive', 'featurediversity': 'positive', 'novelty': 'positive',
                'entropy': 'positive','icov': 'positive', 'dppf': 'positive', 'dpcf': 'positive',
                'giniindex': 'negative', 'mae': 'negative','mpe': 'negative','mse': 'negative','rmse': 'negative',
                'csp': 'negative', 'psp': 'negative','miscalib': 'negative','nonpar': 'negative','valunfairness': 'negative',
                'absunfairness': 'negative','overestimate': 'negative','underestimate': 'negative','ppr': 'negative'        
                }

        self.space = space

        #continuous/discrete function must be readded
        self.discrete = discrete

        self.ranges = Ranges

        self.num_of_vars = num_of_vars

        metric = [elem.text for elem in config._xml_input.xpath('/librec-auto/optimize/metric')][0]

        if metric in self.metric_map:
            self.set_optimization_direction(metric)
        else:
            self.set_optimization_direction(config._xml_input.xpath('/librec-auto/metric/@optimize')[0])

        self.trial = self.study.ask()

    def ask(self):
        self.create_space()
        self.modify_xml(self.space)

    def __str__(self):
        return f"AskCmd()"

    def show(self):
        print(str(self))

    def dry_run(self, config):
        print(f'librec-auto (DR): Running status command {self}')

    def create_space(self):
        print("DISCRETE",self.discrete)
        if self.discrete == None:
            self.space = {self.alphabet[i]: self.trial.suggest_float(self.alphabet[i],self.ranges[i][0], self.ranges[i][1]) for i in range(self.num_of_vars)}
        else:
            self.space = {}
            for i,type in enumerate(self.discrete):
                if type == "continuous":
                    self.space[self.alphabet[i]] = self.trial.suggest_float(self.alphabet[i],self.ranges[i][0], self.ranges[i][1])
                else:
                    self.space[self.alphabet[i]] = self.trial.suggest_int(self.alphabet[i],self.ranges[i][0], self.ranges[i][1])
    
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

    def modify_xml(self, params):
        self.config.write_exp_configs(val = list(params.values()), iteration = self.current_exp_no)

    def execute(self, command):
        self.ask()

    