from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core import ConfigCmd
from librec_auto.core.util import Status
from librec_auto.core.util import Files, create_study_output, BBO, create_log_name, \
    purge_old_logs, InvalidConfiguration, InvalidCommand, UnsupportedFeatureException, \
    LibRecAutoException

class AskCmd(Cmd):
    def __init__(self,Ranges, args, config, current_exp_no, study, ranges, space, num_of_vars, discrete = None, rerank_ranges= None):
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

        self.rerank_ranges = rerank_ranges

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
        print("CREATE SPACE")
        # if len(self.discrete) == 0:
        #     self.space = {self.alphabet[i]: self.trial.suggest_float(self.alphabet[i],self.ranges[i][0], self.ranges[i][1]) for i in range(len(self.ranges))}
        #     print(self.rerank_ranges)
        #     if self.rerank_ranges is not None:
        #         print("entered_range")
        #         for i,type in enumerate(self.rerank_ranges):
        #             if type != "continuous":
        #                 rerank_val = self.trial.suggest_float(self.alphabet[i+self.num_of_vars],self.rerank_ranges[i][0], self.rerank_ranges[i][1])
        #                 print("RERANK VAL", rerank_val)
        #                 self.space[self.alphabet[i+self.num_of_vars-1]] = rerank_val
        #             else:
        #                 rerank_val = self.trial.suggest_int(self.alphabet[i+self.num_of_vars],self.rerank_ranges[i][0], self.rerank_ranges[i][1])
        #                 self.space[self.alphabet[i+self.num_of_vars-1]] = rerank_val
        # else:
        self.space = {}
        self.num_of_vars = len(self.ranges)
        for i,type in enumerate(self.discrete):
            if type == "discrete":
                self.space[self.alphabet[i]] = self.trial.suggest_int(self.alphabet[i],self.ranges[i][0], self.ranges[i][1])
            else:
                self.space[self.alphabet[i]] = self.trial.suggest_float(self.alphabet[i],self.ranges[i][0], self.ranges[i][1])

        #may have to add discrete option for reranking
        if self.rerank_ranges is not None:
            for i,type in enumerate(self.rerank_ranges):
                    rerank_val = self.trial.suggest_float(self.alphabet[i+self.num_of_vars],self.rerank_ranges[i][0], self.rerank_ranges[i][1])
                    self.space[self.alphabet[i+self.num_of_vars]] = rerank_val
                    self.rerank_val = rerank_val

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
        print(self.ranges, self.rerank_ranges)
        print("PARAMS")
        print(params.values())
        print(self.space)
        self.config.write_exp_configs(val = list(params.values()), iteration = self.current_exp_no)

    def execute(self, command):
        self.ask()

    