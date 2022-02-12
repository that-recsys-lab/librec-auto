from librec_auto.core.cmd.eval_cmd import EvalCmd
from librec_auto.core.config_cmd import ConfigCmd
from datetime import datetime
from pathlib import Path
from librec_auto.core import read_config_file
from librec_auto.core.util import Files, create_study_output, BBO, create_log_name, \
    purge_old_logs, InvalidConfiguration, InvalidCommand, UnsupportedFeatureException, \
    LibRecAutoException
from librec_auto.core.cmd import Cmd, SetupCmd, SequenceCmd, PurgeCmd, LibrecCmd, PostCmd, \
                                 RerankCmd, StatusCmd, ParallelCmd, CheckCmd, CleanupCmd, AlgCmd
import logging
from librec_auto.core.util.utils import move_log_file
from librec_auto.core.util.xml_utils import single_xpath
import librec_auto
import os

class compile_commands():

    def __init__(self):
        pass

    def purge_type(self, args: dict) -> str:
        if 'purge' in args:
            return args['purge']
        # If no type specified and you're purging, purge everything
        elif args['action'] == 'purge':
            return 'split'
        else:
            return 'none'

    def build_alg_commands(self,args: dict, config: ConfigCmd, BBO = False):
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


    def build_librec_commands(self, librec_action: str, args: dict, config: ConfigCmd, BBO = False):
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
                else:
                    exp_commands = exp_commands + \
                        [LibrecCmd(librec_action, i) for i in range(BBO)]

            if BBO:
                return exp_commands
            elif threads > 1 and not args['no_parallel']:
                return ParallelCmd(exp_commands, threads)
            else:
                return SequenceCmd(exp_commands)
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
        study_xml = config._xml_input
        script_alg = study_xml.xpath('/study/alg/script')
        if script_alg is not None:
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


        #no describe?
        call_functions_dictionary = {'split': self.split(), 'check': self.check(), 'bbo': self.bbo(), 'split': self.split(), 'purge': self.purge(), 'rerank': self.rerank(), \
        'run': self.run_or_show(), 'show': self.run_or_show(), 'status': self.status(), 'post': self.post(), 'eval': self.eval()}

        function = call_functions_dictionary[self.action]
        function()

        # Set the password in the configuration if we have it
        

    def purge(self): 
        return PurgeCmd(self.purge_type(self.args), no_ask=self.purge_no_ask)

    def status(self):
        return StatusCmd()

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
        # if action == 'split':
            cmd = SequenceCmd([self.build_librec_commands('split', self.args, self.config)])
            bracketed_cmd = self.bracket_sequence('split', self.args, self.config, cmd)
            return bracketed_cmd

    def bbo(self):
        # if action == 'bbo':
            cmd1 = PurgeCmd('results', no_ask=self.purge_no_ask)
            cmd2 = SetupCmd(False)
            cmd3 = [cmd1, cmd2]
            if self.config.has_alg_script():
                cmd_store = self.build_alg_commands(self.args, self.config, BBO=200)
            else:
                cmd_store = self.build_librec_commands('full', self.args, self.config, BBO = 200)
            store_post = [PostCmd() for _ in range(len(cmd_store))]


            init_cmds = [cmd1, cmd2]
            check_cmds = []
            if not self.no_check_flag:
                # check_cmds = [build_librec_commands('check',args,config), CheckCmd()]
                librec_check = self.build_librec_commands('check',self.args,self.config, BBO = 200)
                check_cmds = [librec_check[0], CheckCmd()]
            
            exec_cmds = self.build_librec_commands('full',self.args,self.config, BBO= 200)
            exec_cmds = [SequenceCmd([exec_cmds[i]]) for i in range (len(exec_cmds))]

            if self.rerank_flag:
                # cmd.append(RerankCmd())
                # cmd.append(build_exp_commands('eval', args, config))
                raise UnsupportedFeatureException("Optimization", "Optimization is not currently supported with reranking")

            final_cmds = []

            if self.post_flag:
                final_cmds.append(PostCmd())
            else:
                final_cmds.append(CleanupCmd())

            # cmd = init_cmds + check_cmds + exec_cmds + final_cmds

            cmd = init_cmds + exec_cmds + final_cmds

            return cmd

    def run_or_show(self):
        if self.config.has_alg_script(): 
            self.run_or_show_not_alg_script() 
        else: 
            self.run_or_show_with_alg_script()

    def run_or_show_not_alg_script(self):
        # if (action == 'run' or action == 'show') and not config.has_alg_script():
            cmd1 = self.build_librec_commands('full', self.args, self.config)
            add_eval = self.maybe_add_eval(config=self.config)
            if add_eval:
                # cmd2 = EvalCmd(args, config)  # python-side eval
                cmd2 = self.build_eval_commands(self.args, self.config, self.met_lang)
                cmd = SequenceCmd([cmd1, cmd2])
            else: cmd = SequenceCmd([cmd1])
            if self.rerank_flag:
                cmd.add_command(RerankCmd())
                cmd.add_command(self.build_librec_commands('eval', self.args, self.config))
            # bracketed_cmd = bracket_sequence('results', args, config, cmd)
            bracketed_cmd = self.bracket_sequence('all', self.args, self.config, cmd)
            return bracketed_cmd

    def run_or_show_with_alg_script(self):
        # if (action == 'run' or action == 'show') and config.has_alg_script():
            # if met_lang == 'system':
            cmd1 = self.build_alg_commands(self.args, self.config)
            add_eval = self.maybe_add_eval(config=self.config)
            if add_eval:
                cmd2 = EvalCmd(self.args, self.config)  # python-side eval
                cmd = SequenceCmd([cmd1, cmd2])
            else: cmd = SequenceCmd([cmd1])
            if self.rerank_flag:
                cmd.add_command(RerankCmd())
                cmd.add_command(self.build_librec_commands('eval', self.args, self.config))
            # bracketed_cmd = bracket_sequence('results', args, config, cmd)
            bracketed_cmd = self.bracket_sequence('all', self.args, self.config, cmd)
            return bracketed_cmd

    def eval(self):
        # if action == 'eval':
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

    # The purge rule is: if the command says to run step X, purge the results of X and everything after.
    # def setup_commands(self, args: dict, config: ConfigCmd):
    #     print('args:',args)
        


        # Purge files (possibly) from splits and subexperiments
       

        # Shows the status of the experiment


        # Perform (only) post-processing on results
        
        # No post scripts available

            
        # Perform re-ranking on results, followed by evaluation and post-processing

        # No re-ranker available


        # LibRec actions
        # re-run splits only


        # re-run experiment
       


        # re-run experiment and continue

        


        # eval-only
        

        # check setup of experiment
        # We don't check on algorithm scripts
        


    def bracket_sequence(self, purge_action, args, config, seq_cmd):
        # purge based on what action is being called
        purge_no_ask = args['quiet']
        no_check = args['no_check']
        no_java_check = args['no_java_check']
        post_flag = config.has_post()
        bracketed_commands = []

        # Add purge and setup.
        bracketed_commands.append(PurgeCmd(purge_action, purge_no_ask))
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
