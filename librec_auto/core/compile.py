from bs4 import Script
from librec_auto.core.cmd.eval_cmd import EvalCmd
from librec_auto.core.cmd.ask_cmd import AskCmd
from librec_auto.core.cmd.tell_cmd import TellCmd
from librec_auto.core.config_cmd import ConfigCmd
from datetime import datetime
from pathlib import Path
from librec_auto.core import read_config_file
from librec_auto.core.util import Files, create_study_output, BBO, create_log_name, \
    purge_old_logs, InvalidConfiguration, InvalidCommand, UnsupportedFeatureException, \
    LibRecAutoException
from librec_auto.core.util.BBO import RepeatPruner
from librec_auto.core.cmd import Cmd, SetupCmd, SequenceCmd, PurgeCmd, LibrecCmd, PostCmd, \
                                 RerankCmd, StatusCmd, ParallelCmd, CheckCmd, CleanupCmd, AlgCmd
import logging
from librec_auto.core.util.utils import move_log_file
from librec_auto.core.util.xml_utils import single_xpath
import librec_auto
import optuna
import os



class compile_commands():

    def __init__(self):
        self.iterations = None
        self.startpos = None

    def purge_type(self, args: dict) -> str:
        if 'purge' in args:
            return args['purge']
        # If no type specified and you're purging, purge everything
        elif args['action'] == 'purge':
            return 'split'
        else:
            return 'none'

    def build_alg_commands(self,args: dict, config: ConfigCmd, BBO = False):
        print("building")
        threads = config.thread_count()

        # Need to split because normally librec does that
        exp_commands = [LibrecCmd('split', 0)]
        exp_range = range(BBO) if BBO else range(config.get_sub_exp_count())

        try:
            for i in exp_range:
                alg_cmd = AlgCmd(i)
                eval_cmd = LibrecCmd('eval', i) # Need eval after each experiment
                alg_seq = SequenceCmd([alg_cmd, eval_cmd])
                exp_commands.append(alg_seq)

            if BBO:
                return exp_commands
            elif threads > 1 and not args['no_parallel']:
                return ParallelCmd(exp_commands, threads)
            else:
                return SequenceCmd(exp_commands)
        except:
            raise LibRecAutoException("Building Alg Commands",
                                    f"While building alg command an error was thrown.")

    #perhaps a placeholder
    def build_ask_tell_alg_commands(self,args: dict, config: ConfigCmd, BBO = False, startpos = 0):
        threads = config.thread_count()

        # Need to split because normally librec does that
        exp_commands = [LibrecCmd('split', 0)]
        exp_range = range(BBO) if BBO else range(config.get_sub_exp_count())
        print("ALGS")
        try:
            study = optuna.create_study(pruner=RepeatPruner())

            #maybe seperate into additional function?
            parameter_space = {}        
            vconf = config._var_coll.var_confs
            num_of_vars = len([0 for var in vconf[0].vars])

            range_val_store = [[i.val for i in j.vars if i.type == 'librec'] for j in vconf]
            range_val_store = [[float(array[i]) for array in range_val_store] for i in range(len(range_val_store[0]))]
            ranges = [[min(array), max(array)] for array in range_val_store]
            for i in range(startpos, self.iterations):
                ask = AskCmd(self.args, self.config, i, study, ranges, parameter_space, num_of_vars)
                trial = ask.trial()
                alg_cmd = AlgCmd(i)
                eval_cmd = LibrecCmd('eval', i) # Need eval after each experiment
                alg_seq = SequenceCmd([alg_cmd, eval_cmd])
                tell = TellCmd(study, self.args, self.config, i, study, trial, files = self.files)
                seq = SequenceCmd([ask, alg_seq, tell])
                exp_commands.append(seq)

            return SequenceCmd(exp_commands)
        except:
            raise LibRecAutoException("Building Alg Commands",
                                    f"While building alg command an error was thrown.")

    def build_librec_commands(self, librec_action: str, args: dict, config: ConfigCmd, BBO = False, startpos = 0):
        threads = config.thread_count()
        if librec_action == 'full':
            exp_commands = [LibrecCmd('split', 0)]
        else:
            exp_commands = []

        try:
            if BBO is False:
                exp_commands = exp_commands + \
                    [LibrecCmd(librec_action, i) for i in range(config.get_sub_exp_count())]

            else:
                if librec_action == 'check':
                    exp_commands =  exp_commands + [LibrecCmd(librec_action, 0)]
                elif librec_action == 'eval':
                    exp_commands =  exp_commands + [LibrecCmd(librec_action, BBO, write_config = False)]
                else:
                    exp_commands = exp_commands + \
                        [LibrecCmd(librec_action, BBO)]

            if BBO is not False:
                return exp_commands
            elif threads > 1 and not args['no_parallel']:
                return ParallelCmd(exp_commands, threads)
            else:
                return SequenceCmd(exp_commands)
        except:
            raise LibRecAutoException("Building Librec Commands",
                                    f"While building librec command {librec_action}, a script failed")

    #likely will delete later, need this as a placeholder
    def build_librec_ask_tell(self, librec_action: str, args: dict, config: ConfigCmd, startpos = 0):
        # threads = config.thread_count()
        if librec_action == 'full':
            exp_commands = [LibrecCmd('split', startpos)]
        else:
            exp_commands = []


        try:
            if librec_action == 'check':
                exp_commands =  exp_commands + [LibrecCmd(librec_action, startpos)]
            else:
                study = optuna.create_study(pruner=RepeatPruner())
                file_num = str(startpos)
                while len(file_num) < 5:
                    file_num = "0" + str(file_num)

                if startpos != 0:
                    study = optuna.load_study(study_name = self.files._study_path + "/" + "exp" + file_num)
                addition_exp_commands = []
                parameter_space = {}        
                vconf = config._var_coll.var_confs
                num_of_vars = len([0 for var in vconf[0].vars])

                value_store = [[(i.path,i.val) for i in j.vars if i.type == 'librec'] for j in vconf]
                rerank_value_store = [[(i.path,i.val) for i in j.vars if i.type == 'rerank'] for j in vconf]
                value_store_dict = {}
                rerank_value_store_dict = {}

                for arr in value_store:
                    for item in arr:
                        path, val = item[0],item[1]
                        if path not in value_store_dict:
                            value_store_dict[path] = []
                        value_store_dict[path].append(val)

                for val in value_store_dict.keys():
                    arr = value_store_dict[val]
                    arr = [float(i) for i in arr]
                    value_store_dict[val] = [min(arr), max(arr)]


                for arr in rerank_value_store:
                    for item in arr:
                        path, val = item[0],item[1]
                        if path not in rerank_value_store_dict:
                            rerank_value_store_dict[path] = []
                        rerank_value_store_dict[path].append(val)

                for val in rerank_value_store_dict.keys():
                    arr = rerank_value_store_dict[val]
                    arr = [float(i) for i in arr]
                    rerank_value_store_dict[val] = [min(arr), max(arr)]

                discrete_optimization = {elem.getparent().tag: "discrete" if elem.getparent().get("type") is not None else "continuous" for elem in config._xml_input.xpath('/librec-auto/alg/*/lower')}

                key_split = {i:i.split('/')[-1] for i in value_store_dict.keys()}
                
                continuous = {path:value_store_dict[path] for path in value_store_dict.keys() if discrete_optimization[key_split[path]] == "continuous"}
                discrete = {path:value_store_dict[path] for path in value_store_dict.keys() if discrete_optimization[key_split[path]] == "discrete"}

                iterations = [elem.text for elem in config._xml_input.xpath('/librec-auto/optimize/iterations')][0]
                optimize_val = None
                if len([elem.text for elem in config._xml_input.xpath('/librec-auto/optimize/previous-max')]) > 0:
                    optimize_val = [elem.text for elem in config._xml_input.xpath('/librec-auto/optimize/previous-max')][0]
                for i in range(startpos, int(iterations)):
                    print(i)
                    ask = AskCmd(self.args, self.config, i, study, parameter_space, num_of_vars, continuous = continuous, discrete = discrete, rerank_ranges = rerank_value_store_dict)
                    trial = ask.trial
                    execute = LibrecCmd("full", i)


                    #if rerank, add reranking step here
                    # self, args, config, current_exp_no, study, trial, metric, direction)
                    tell = None
                    rerank1 = None
                    rerank2 = None

                    platform = self.execution_platform(self.config, "metric")
                    if (platform == "system" or platform == "both") and self.rerank_flag:
                      r = EvalCmd(self.args, self.config, curr_exp = i) 
                      rerank1 = RerankCmd(exp_no = i)
                      rerank1 = SequenceCmd([r, rerank1])
                      rerank2 = self.build_librec_commands('eval', self.args, self.config, BBO = i)
                      cmd2 = EvalCmd(self.args, self.config, curr_exp = i)  # python-side evaluation
                      tell = TellCmd(self.args, self.config, i, study, trial, ask.metric, ask.direction, old_librec_value_command = r, new_val = cmd2, optimize_val = optimize_val, files = self.files)
                      tell = SequenceCmd([cmd2,tell])
                      rerank = SequenceCmd([rerank1, SequenceCmd(rerank2)])

                    elif self.rerank_flag:
                      rerank1 = RerankCmd(exp_no = i)
                      rerank2 = self.build_librec_commands('eval', self.args, self.config, BBO = i)
                      tell = TellCmd(self.args, self.config, i, study, trial, ask.metric, ask.direction, old_librec_value_command = rerank2[0], hack = True, files = self.files)
                      rerank = SequenceCmd([rerank1, SequenceCmd(rerank2)])

                    #python metric
                    elif platform == "system" or platform == "both":
                      cmd2 = EvalCmd(self.args, self.config, curr_exp = i)  # python-side eval
                      tell = TellCmd(self.args, self.config, i, study, trial, ask.metric, ask.direction, files = self.files)
                      tell = SequenceCmd([cmd2,tell])

                    else:
                      tell = TellCmd(self.args, self.config, i, study, trial, ask.metric, ask.direction, files = self.files)

                    seq = None
                    if self.rerank_flag:
                        seq = SequenceCmd([ask, execute, rerank, tell])
                    else:
                        seq = SequenceCmd([ask, execute, tell])

                    
                    addition_exp_commands.append(seq)

                exp_commands += addition_exp_commands
                return [SequenceCmd(exp_commands)]
        except:
            raise LibRecAutoException("Building Librec Commands",
                                    f"While building librec command {librec_action}, a script failed")

    def build_eval_commands(self, args: dict, config: ConfigCmd, execution: str):
        '''
        function to build the seqeunce of eval commands based on where they'll be executed
        '''
        experiment_cmds = None
        if execution == 'system':
            experiment_cmds = [EvalCmd(args, config)]
        if execution == 'both':
            experiment_cmds = [self.build_librec_commands('eval', args, config), EvalCmd(args, config)]
        # third option: if librec
        if execution == 'librec':
            experiment_cmds = [self.build_librec_commands('eval', args, config)]

        return SequenceCmd(experiment_cmds)

    def maybe_add_eval(self, config: ConfigCmd):
        if len(self.script_alg) > 0:
            return True
        elif len(self.study_xml.xpath('/librec-auto/metric/script')) > 0:
            return True
        else: return False

    def execution_platform(self, config: ConfigCmd, section: str) -> str:
        '''
        pass in section to examine what platform will be used for execution
        params:
            config: config object
            section: string, name of section to examine
        returns:
            'librec': if section uses librec
            'system': if section uses script
            'both': if section has both librec and system executables
        '''
        study_xml = config._xml_input
        #need to relocate
        config_section = study_xml.xpath(f'/librec-auto/{section}/script')

        # if something returns from xpath
        if config_section:
            # for metric, could have both librec and system metrics
            # look for scripts and classes, return either script, class, or both
            if section == 'metric':
                # get the children
                # have to check siblings before and after 'config_section' element
                for sib in config_section[0].itersiblings(preceding=True):
                    # if there are only other script tags, then return 'system'
                    # if there's anything else, return 'both'
                    if sib.tag != 'script':
                        return 'both'

                for sib in config_section[0].itersiblings():
                    if sib.tag != 'script':
                        return 'both'
                
                return 'system'
                # if it's only a script then the length of getchildren will be 1: <script>
            else:
                # if section is <alg> then there can only be one algorithm provided
                # if config_section is not none, then the algorithm must be a script
                return 'system'
        
        # should only enter if user doesn't include a script, meaning librec only
        else:
            return 'librec'

    def setup_commands(self, args: dict, config: ConfigCmd):
        self.args = args
        self.config = config
        self.action = args['action']
        self.purge_no_ask = args['quiet']

        #generally returns 'librec' if there is no script
        self.alg_lang = self.execution_platform(config, 'alg')
        self.met_lang = self.execution_platform(config, 'metric')
        # Create flags for optional steps
        self.rerank_flag = config.has_rerank()
        self.post_flag = config.has_post()

        # Flag to use/avoid check
        # if true, user specified don't run check, else, run check.
        self.no_check_flag = args['no_check']
        if args['key_password']:
            config.set_key_password(args['key_password'])

        self.bbo_flag = False
        if args['action'] == 'bbo':
            self.bbo_flag = True

        self.study_xml = config._xml_input
        self.script_alg = self.study_xml.xpath('/study/alg/script')

        config_file = Files.DEFAULT_CONFIG_FILENAME

        if self.args['conf']:  # User requested a different configuration file from the default
            config_file = self.args['conf']

        target = ""
        if (self.args['target'] != None):
            target = self.args['target']
        
        log_file = self.args['log_name']

        # create a path: 
        
        self.co = read_config_file(config_file, target, log_file)
        self.files = self.co._files

        #no describe?
        call_functions_dictionary = {'split': self.split, 'check': self.check, 'bbo': self.new_bbo, 'split': self.split, 'purge': self.purge, 'rerank': self.rerank, \
        'run': self.run_or_show, 'show': self.run_or_show, 'status': self.status, 'post': self.post, 'eval': self.eval, 'resume':self.resume}

        function = call_functions_dictionary[self.action]

        if 'show_bbo' in args:
            function = call_functions_dictionary['bbo']
            
        return function()

        # Set the password in the configuration if we have it
        

    def purge(self): 
        return PurgeCmd(self.purge_type(self.args), no_ask=self.purge_no_ask)

    def status(self):
        return StatusCmd()

    def resume(self):
        # self.
        folder_count = 0
        folder_to_resume = -1
        for folder in os.listdir(self.co._files._study_path):
            if folder == "temp" or folder == "conf" or os.path.isfile(str(self.co._files._study_path)+ '/' + str(folder)):
                continue
            
            output_xml = "output.xml"
            break_loop = True
            if len(os.listdir(str(self.co._files._study_path) + '/' + str(folder))) == 0:
                break_loop = False
            for file in os.listdir(str(self.co._files._study_path) + '/' + str(folder)):
                
                folder_to_resume = str(self.co._files._study_path) + '/' + str(folder)
                if output_xml == file:
                    break_loop = False
            folder_count += 1
            if break_loop == True:
                break
        
        print("startpos", folder_count)
        self.startpos = folder_count
        return self.new_bbo()


    def post(self):
        if self.post_flag:
            return PostCmd()
        else:
            raise InvalidCommand(self.action, "No post-processing scripts available for \"post\" command")

    def rerank(self): 
        if self.rerank_flag:  # Runs a reranking script on the python side
            cmd1 = RerankCmd()
            cmd2 = self.build_librec_commands('eval', self.args, self.config)
            cmd3 = EvalCmd(self.args, self.config)  # python-side eval
            cmd = SequenceCmd([cmd1, cmd2, cmd3])
            
            bracketed_cmd = self.bracket_sequence('rerank', self.args, self.config, cmd)
            return bracketed_cmd

        else:
            raise InvalidCommand(self.action, "No re-ranker scripts available for \"rerank\" command.")
            
            

    def split(self):
        cmd = SequenceCmd([self.build_librec_commands('split', self.args, self.config)])
        bracketed_cmd = self.bracket_sequence('split', self.args, self.config, cmd)
        return bracketed_cmd

    def new_bbo(self):
        cmd1 = PurgeCmd('results', no_ask=self.purge_no_ask)
        cmd2 = SetupCmd(False)
        init_cmds = [cmd1, cmd2]

        check_cmds = []
        # if not self.no_check_flag:
        #         librec_check = self.build_librec_commands('check', self.args, self.config, BBO = 200)
        #         check_cmds = [librec_check[0], CheckCmd()]
        
        exec_cmds = []
        # print("BEFORE ALG SCRIPT", self.config.has_alg_script())
        startpos = 0
        # print("before adk_tell_call")
        if self.startpos is not None:
            startpos = self.startpos
            init_cmds = []
        if self.config.has_alg_script():
            exec_cmds = self.build_ask_tell_alg_commands(self.args, self.config, startpos=startpos)
        else:
            exec_cmds = self.build_librec_ask_tell('full', self.args, self.config, startpos=startpos)

        final_cmds = []

        if self.post_flag:
            final_cmds.append(CleanupCmd())
            final_cmds.append(PostCmd())
        else:
            final_cmds.append(CleanupCmd())

        cmd = init_cmds + check_cmds + exec_cmds + final_cmds
        return cmd

    def run_or_show(self):

        cmd1 = self.build_librec_commands('full', self.args, self.config)
        add_eval = self.maybe_add_eval(config=self.config)

        # print(add_eval, self.config.has_alg_script(), self.config.has_metric_script())
        if add_eval and not self.config.has_alg_script() and not self.config.has_metric_script():
            cmd2 = self.build_eval_commands(self.args, self.config, self.met_lang) 
            cmd = SequenceCmd([cmd1, cmd2])
        elif add_eval and not self.config.has_alg_script():
            # cmd =  SequenceCmd([cmd1, self.build_eval_commands(self.args, self.config, self.met_lang),EvalCmd(self.args, self.config)])
            cmd =  SequenceCmd([cmd1,EvalCmd(self.args, self.config)])
        elif add_eval:
            cmd1 = self.build_alg_commands(self.args, self.config)
            cmd2 = EvalCmd(self.args, self.config)  # python-side eval
            cmd = SequenceCmd([cmd1, cmd2])
        else: 
            cmd = SequenceCmd([cmd1])
        if self.rerank_flag:
            cmd.add_command(RerankCmd())
            cmd.add_command(self.build_librec_commands('eval', self.args, self.config))
        # bracketed_cmd = bracket_sequence('results', args, config, cmd)
        bracketed_cmd = self.bracket_sequence('all', self.args, self.config, cmd)
        return bracketed_cmd

    def eval(self):
        # if action == 'eval':
            #maybe get this to work later
            if single_xpath(self.config.get_xml(), '/librec-auto/optimize') is not None:
                raise InvalidConfiguration("Eval-only not currently supported with Bayesian optimization.")

            # cmd1 = PurgeCmd('post', no_ask=purge_no_ask)
            # cmd2 = SetupCmd()
            cmd1 = self.build_librec_commands('eval', self.args, self.config)
            cmd2 = EvalCmd(self.args, self.config)  # python-side eval
            cmd = SequenceCmd([cmd1, cmd2])
            bracketed_cmd = self.bracket_sequence('post', self.args, self.config, cmd)
            return bracketed_cmd

    def check(self):
        # if action == 'check':
            cmd1 = self.build_librec_commands('check', self.args, self.config)
            cmd2 = CheckCmd()
            cmd = SequenceCmd([cmd1, cmd2])
            bracketed_cmd = self.bracket_sequence('none', self.args, self.config, cmd)
            return bracketed_cmd

    def bracket_sequence(self, purge_action, args, config, seq_cmd):
        # purge based on what action is being called
        purge_no_ask = args['quiet']
        no_check = args['no_check']
        no_java_check = args['no_java_check']
        post_flag = config.has_post()
        bracketed_commands = []

        # Add purge and setup.
        bracketed_commands.append(PurgeCmd(purge_action, purge_no_ask))
        if self.bbo_flag:
            bracketed_commands.append(SetupCmd(no_java_flag=no_java_check, startflag = True))
        else:
            bracketed_commands.append(SetupCmd(no_java_flag=no_java_check))
        if not no_check:
            bracketed_commands.append(self.build_librec_commands('check', args, config))
            bracketed_commands.append(CheckCmd())
        # Add passed sequence of commands.
        bracketed_commands.append(seq_cmd)
        # Create an output xml file.
        if post_flag:
            bracketed_commands.append(PostCmd())
        else:
            bracketed_commands.append(CleanupCmd())
        # Convert entire list to SequenceCmd object.
        new_cmd = SequenceCmd(bracketed_commands)
        return new_cmd
