from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core import ConfigCmd
from librec_auto.core.util import Status
from librec_auto.core.util import Files, create_study_output, BBO, create_log_name, \
    purge_old_logs, InvalidConfiguration, InvalidCommand, UnsupportedFeatureException, \
    LibRecAutoException

class AskCmd(Cmd):
    def __init__(self,args, config, current_exp_no, study, space, num_of_vars, continuous = None, discrete = None, rerank_ranges= None):
        # print("init")
        self.config = config
        self.args = args 
        self.current_exp_no = current_exp_no
        self.study = study
        self.status = 3
        self.continuous = continuous
        self.discrete = discrete
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
        self.continuous = continuous

        self.discrete = discrete

        self.rerank_ranges = rerank_ranges

        self.num_of_vars = num_of_vars

        metric = [elem.text for elem in config._xml_input.xpath('/librec-auto/optimize/metric')][0]
        self.metric = metric
        if metric in self.metric_map:
            self.set_optimization_direction(metric)
        else:
            if len(config._xml_input.xpath('/librec-auto/metric/@optimize')) == 0:
                self.set_optimization_direction("higher")
            else:
                self.set_optimization_direction(config._xml_input.xpath('/librec-auto/metric/@optimize')[0])

        self.trial = self.study.ask()

    def ask(self):
        self.create_space()
        self.modify_xml(self.space)
    #     self.try_hack()

    # def try_hack(self):
    #     i = 0
    #     for sub_paths in self.config._files.get_exp_paths_iterator():
    #         if i != self.current_exp_no:
    #             i += 1
    #             continue

    #         status = Status(sub_paths)
    #         print("PRIOR STATUS", status.get_metric_info(status._log, BBO = True))

    def __str__(self):
        return f"AskCmd()"

    def show(self):
        print(str(self))

    def dry_run(self, config):
        print(f'librec-auto (DR): Running status command {self}')

    def create_space(self):
        self.space = {}
        #ranges, rerank_ranges become dictionaries of ranges

        for i,type in enumerate(self.continuous.keys()):
            self.space[type] = self.trial.suggest_float(type,self.continuous[type][0], self.continuous[type][1])

        for i,type in enumerate(self.discrete.keys()):
            self.space[type] = self.trial.suggest_int(type,self.discrete[type][0], self.discrete[type][1])

        #may have to add discrete option for reranking
        if self.rerank_ranges is not None:
            for i,type in enumerate(self.rerank_ranges.keys()):
                    rerank_val = self.trial.suggest_float(type,float(self.rerank_ranges[type][0]), float(self.rerank_ranges[type][1]))
                    self.space[type] = rerank_val
                    self.rerank_val = rerank_val

    def set_optimization_direction(self, metric):
        # self.metric = metric
        # print("self.metric",self.metric)
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
        self.config.write_exp_configs(val = params, iteration = self.current_exp_no)


    def execute(self, command):
        self.ask()

    