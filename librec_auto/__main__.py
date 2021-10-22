import argparse
from librec_auto.core.cmd.eval_cmd import EvalCmd
from librec_auto.core.config_cmd import ConfigCmd
from datetime import datetime
from pathlib import Path
from librec_auto.core import read_config_file
from librec_auto.core.util import Files, create_study_output, BBO, create_log_name, \
    purge_old_logs, InvalidConfiguration, InvalidCommand, UnsupportedFeatureException, \
    LibRecAutoException
from librec_auto.core.cmd import Cmd, SetupCmd, SequenceCmd, PurgeCmd, LibrecCmd, PostCmd, \
                                 RerankCmd, StatusCmd, ParallelCmd, CheckCmd, CleanupCmd
import logging
from librec_auto.core.util.utils import move_log_file
import librec_auto
import os


def read_args():
    '''
    Parse command line arguments.
    :return:
    '''
    parser = argparse.ArgumentParser(
        description=
        'The librec-auto tool for running recommender systems experiments.',
        epilog=
        'TODO- This is a work in progress. For now, refer to this link: https://librec-auto.readthedocs.io/en/latest/'
    )

    # todo remove py-eval AS
    parser.add_argument('action',
                        choices=[
                            'run', 'split', 'eval', 'rerank', 'post', 'purge',
                            'status', 'describe', 'check', 'py-eval'
                        ])

    parser.add_argument("-t", "--target", help="Path to experiment directory")

    # Optional with arguments
    parser.add_argument("-c",
                        "--conf",
                        help="Use the specified configuration file")

    # Flags
    parser.add_argument(
        "-dr",
        "--dry_run",
        help="Show sequence of command execution but do not execute commands",
        action="store_true")

    parser.add_argument("-q",
                        "--quiet",
                        help="Skip confirmation when purging",
                        action="store_true")

    parser.add_argument(
        "-np",
        "--no_parallel",
        help=
        "Ignore thread-count directive and run all operations sequentially",
        action="store_true")

    parser.add_argument(
        "-p",
        "--purge",
        help="Purge results of step given in <option> and all subsequent steps",
        choices=['all', 'split', 'results', 'rerank', 'post'],
        default='all')

    parser.add_argument(
        "-dev",
        "--dev",
        help="Help with documentation, code formatting, and Docker",
        action="store_true")

    parser.add_argument("-HT",
                        "--HT",
                        help="Help with using libraries (Not implemented)",
                        action="store_true")

    parser.add_argument(
        "-PCO",
        "--PCO",
        help="Help with producting CSV outputs (Not implemented)",
        action="store_true")

    parser.add_argument("-int",
                        "--int",
                        help="Help with Integrations (Not implemented)",
                        action="store_true")

    parser.add_argument(
        "-k",
        "--key_password",
        help="Password for the API keys used by post-processing scripts")

    parser.add_argument(
        "-nc",
        "--no_check",
        help="Don't run the check command",
        action="store_true")

    parser.add_argument(
        "-nj",
        "--no_java_check",
        help="Don't run the java check",
        action="store_true")


    input_args = parser.parse_args()
    error_check(vars(input_args))
    return vars(input_args)

def error_check(input_arguments: dict):
    if input_arguments['target'] == None:
        raise InvalidCommand("Missing instruction", "Target (-t) argument missing from command line instruction\n"\
            "To use current directory, use \"-t .\", or for a specific directory use \"-t <directory-name>\"")

def load_config(args: dict) -> ConfigCmd:

    config_file = Files.DEFAULT_CONFIG_FILENAME

    if args['conf']:  # User requested a different configuration file from the default
        config_file = args['conf']

    target = ""
    if (args['target'] != None):
        target = args['target']
    
    log_file = args['log_name']

    # create a path: 
    
    return read_config_file(config_file, target, log_file)


DESCRIBE_TEXT = 'Librec-auto automates recommender systems experimentation using the LibRec Java library.\n' +\
    '\tA librec-auto experiment consist of five steps governed by the specifications in the configuration file:\n' +\
    '\t- split: Create training / test splits from a data set. (LibRec)\n' +\
    '\t- exp: Run an experiment generating recommendations for a test set (LibRec)\n' +\
    '\t- rerank (optional): Re-rank the results of the experiment (script)\n' +\
    '\t- eval: Evaluate the results of a recommendation experiment (LibRec)\n' +\
    '\t- post (optional): Perform post-processing computations (script)\n' + \
    'Steps labeled LibRec are performed by the LibRec library using configuration properties generated by librec-auto.\n' +\
    'Steps labeled script are performed by experimenter-defined scripts.\n' + \
    'Run librec_auto describe <step> for additional information about each option.'

DESCRIBE_DICT = {
    'run':
    'Run a complete librec-auto experiment. Re-uses cached results if any. \
May result in no action if all computations are up-to-date and no purge option is specified.',
    'split': 'Run the training / test split only',
    'exp': 'Run the experiment, re-ranking, evaluation, and post-processing',
    'rerank': 'Run the re-ranking, evaluation and post-processing',
    'eval': 'Run the evaluation and post-processing',
    'post': 'Run post-processing steps',
    'purge':
    'Purge cached computations. Uses -p flag to determine what to purge',
    'status': 'Print out the status of the experiments'
}


def print_description(args: dict) -> None:
    act = args['target']
    if act in DESCRIBE_DICT:
        print(f'core {act} <target>: {DESCRIBE_DICT[act]}')
    else:
        print(DESCRIBE_TEXT)


def purge_type(args: dict) -> str:
    if 'purge' in args:
        return args['purge']
    # If no type specified and you're purging, purge everything
    elif args['action'] == 'purge':
        return 'split'
    else:
        return 'none'


# TODO: Need to rewrite as "build_exec_commands" where the action incorporates both execution
# and reranking. Remember that the re-ranker only requires one run of the prediction algorithm for any
# variation its own parameters.
def build_librec_commands(librec_action: str, args: dict, config: ConfigCmd, BBO = False):
    librec_commands = []
    threads = config.thread_count()

    try:
        if BBO is False:
            librec_commands = [
                LibrecCmd(librec_action, i) for i in range(config.get_sub_exp_count())
            ]
        else:
            librec_commands = [
                LibrecCmd(librec_action, i) for i in range(BBO)
            ]

        if BBO:
            return librec_commands
        elif threads > 1 and not args['no_parallel']:
            return ParallelCmd(librec_commands, threads)
        else:
            return SequenceCmd(librec_commands)
    except:
        raise LibRecAutoException("Building Librec Commands", 
                                  f"While building librec command {librec_action}, a script failed")

    


# The purge rule is: if the command says to run step X, purge the results of X and everything after.
def setup_commands(args: dict, config: ConfigCmd):
    action = args['action']
    purge_no_ask = args['quiet']

    # Create flags for optional steps
    rerank_flag = config.has_rerank()
    post_flag = config.has_post()

    # Flag to use/avoid check
    # if true, user specified don't run check, else, run check.
    no_check_flag = args['no_check']

    # Set the password in the configuration if we have it
    if args['key_password']:
        config.set_key_password(args['key_password'])

    # Purge files (possibly) from splits and subexperiments
    if action == 'purge':
        return PurgeCmd(purge_type(args), no_ask=purge_no_ask)

    # Shows the status of the experiment
    if action == 'status':
        return StatusCmd()

    # Perform (only) post-processing on results
    if action == 'post' and post_flag:
        return PostCmd()
    # No post scripts available
    if action == 'post' and not post_flag:
        raise InvalidCommand(action, "No post-processing scripts available for \"post\" command")
        
    # Perform re-ranking on results, followed by evaluation and post-processing
    if action == 'rerank' and rerank_flag:  # Runs a reranking script on the python side
        cmd1 = RerankCmd()
        cmd2 = build_librec_commands('eval', args, config)
        cmd3 = EvalCmd(args, config)  # python-side eval
        cmd = SequenceCmd([cmd1, cmd2, cmd3])
        
        bracketed_cmd = bracket_sequence('rerank', args, config, cmd)
        return bracketed_cmd
    # No re-ranker available
    if action == 'rerank' and not rerank_flag:
        raise InvalidCommand(action, "No re-ranker scripts available for \"rerank\" command.")

    # LibRec actions
    # re-run splits only
    if action == 'split':
        cmd = SequenceCmd([build_librec_commands('split', args, config)])
        bracketed_cmd = bracket_sequence('split', args, config, cmd)
        return bracketed_cmd

    # re-run experiment
    if action == 'bbo':
        cmd1 = PurgeCmd('results', no_ask=purge_no_ask)
        cmd2 = SetupCmd()
        cmd3 = [cmd1, cmd2]
        cmd_store = build_librec_commands('full', args, config, BBO = 200)
        store_post = [PostCmd() for _ in range(len(cmd_store))]

        for i in range(len(cmd_store)):
            cmd3.append(cmd_store[i])

        cmd = [SequenceCmd([cmd3[i]]) for i in range (2,len(cmd3))]
        cmd = [cmd1, cmd2] + cmd

        if rerank_flag:
            # cmd.append(RerankCmd())
            # cmd.append(build_librec_commands('eval', args, config))
            raise UnsupportedFeatureException("Optimization", "Optimization is not currently supported with reranking")
        if post_flag:
            cmd.append(PostCmd())

        if not no_check_flag:
            cmd[2:2] = [build_librec_commands('check', args, config), CheckCmd()]

        return cmd


    # re-run experiment and continue
    if action == 'run':
        cmd1 = build_librec_commands('full', args, config)
        cmd2 = EvalCmd(args, config)  # python-side eval
        cmd = SequenceCmd([cmd1, cmd2])
        if rerank_flag:
            cmd.add_command(RerankCmd())
            cmd.add_command(build_librec_commands('eval', args, config))
        bracketed_cmd = bracket_sequence('results', args, config, cmd)
        return bracketed_cmd

    # eval-only
    if action == 'eval':
        # cmd1 = PurgeCmd('post', no_ask=purge_no_ask)
        # cmd2 = SetupCmd()
        cmd1 = build_librec_commands('eval', args, config)
        cmd2 = EvalCmd(args, config)  # python-side eval
        cmd = SequenceCmd([cmd1, cmd2])
        bracketed_cmd = bracket_sequence('post', args, config, cmd)
        return bracketed_cmd

    # # Running python side evaluation
    # if action == 'py-eval':
    #     cmd = SequenceCmd([EvalCmd(args, config)])
    #     if post_flag:
    #         cmd.add_command(PostCmd())
    #     return cmd

    # check setup of experiment
    if action == 'check':
        cmd1 = build_librec_commands('check', args, config)
        cmd2 = CheckCmd()
        cmd = SequenceCmd([cmd1, cmd2])
        bracketed_cmd = bracket_sequence('none', args, config, cmd)
        return bracketed_cmd

def bracket_sequence(purge_action, args, config, seq_cmd):
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
        bracketed_commands.append(build_librec_commands('check', args, config))
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

# -------------------------------------

if __name__ == '__main__':
    
    args = read_args()
        
    # purge_old_logs(args['target'] + "/*")
    log_name = create_log_name('LibRec-Auto_log{}.log')
    args['log_name'] = log_name
    librec_auto_log = str(Path(args['target']) / args['log_name'])
    if args['dev']:
        logging.basicConfig(filename=librec_auto_log,filemode='w',level=logging.DEBUG)
    else:
        logging.basicConfig(filename=librec_auto_log,filemode='w',level=logging.WARNING)

    jar_path = Path(librec_auto.__file__).parent / "jar" / "auto.jar"
    if not jar_path.is_file():
        print("Error: LibRec JAR file is missing.")

    else:
        if args['action'] == 'describe':
            print_description(args)
        elif args['action'] == 'check':
            config = load_config(args)
            move_log_file(config)
            if config.is_valid():
                try:
                    command = setup_commands(args, config)
                except LibRecAutoException:
                    print("Exception caught, check output.xml file.")
                    logging.shutdown()
                    clean = CleanupCmd()
                    clean.execute(config)
                    exit(-1)
                
                if args['dry_run']:
                    command.dry_run(config)
                else:
                    try: 
                        command.execute(config)
                    except LibRecAutoException:
                        print("Exception caught, check output.xml file.")
                        logging.shutdown()
                        clean = CleanupCmd()
                        clean.execute(config)
                        exit(-1)
        else:
            config = load_config(args)
            
            if config.is_valid():
                try:
                    command = setup_commands(args, config)
                except LibRecAutoException:
                    print("Exception caught, check output.xml file.")
                    logging.shutdown()
                    clean = CleanupCmd()
                    clean.execute(config)
                    exit(-1)

                if len(config._xml_input.xpath('/librec-auto/alg//*/lower')) >0 and \
                        (args['action'] == 'run' or args['action'] == 'dry_run'):
                    if args['action'] == 'run':
                        args['action'] = 'bbo'
                    print('Running BBO. Recreating Config.')
                    config = load_config(args)
                    command = setup_commands(args, config)

                if isinstance(command, Cmd):
                    if args['dry_run']:
                        command.dry_run(config)
                    else:
                        try: 
                            command.execute(config)
                        except LibRecAutoException:
                            print("Exception caught, check output.xml file.")
                            logging.shutdown()
                            clean = CleanupCmd()
                            clean.execute(config)
                            exit(-1)
                            


                elif isinstance(command, list):
                    vconf = config._var_coll.var_confs

                    num_of_vars = len([0 for var in vconf[0].vars])
                    
                    range_val_store = [[i.val for i in j.vars if i.type == 'librec'] for j in vconf]

                    range_val_store = [[float(array[i]) for array in range_val_store] for i in range(len(range_val_store[0]))]

                    range_val_store = [[min(array), max(array)] for array in range_val_store]

                    check_rerank = len([elem.text for elem in config._xml_input.xpath('/librec-auto/rerank/*//lower')])

                    if check_rerank > 0:
                        raise InvalidConfiguration("Optimization", "Optimization is not currently supported with reranking")

                    exponent_expected = num_of_vars

                    for tup in range_val_store:
                        if tup[0] == tup[1]:
                            exponent_expected -= 1

                   # if 2**exponent_expected == config.get_sub_exp_count():
                        range_list = [(range_val_store[i][0],range_val_store[i][1]) for i in range(len(range_val_store))]
                        value_elems = [elem.text for elem in config._xml_input.xpath('/librec-auto/optimize/iterations')]

                        continue_rerank = False

                        if isinstance(command[-2], RerankCmd):

                            final_commands = command[-2:]

                            command = command[:int(value_elems[0])+2]

                            continue_rerank = True

                            command = command + final_commands

                        bbo = BBO.BBO(range_list, len(range_val_store), command[2:], config)
                        file_path = bbo.run_purge(command[0])

                        metric = [elem.text for elem in config._xml_input.xpath('/librec-auto/optimize/metric')][0]

                        if metric in bbo.metric_map:
                            bbo.set_optimization_direction(metric)
                        else:
                            bbo.set_optimization_direction(config._xml_input.xpath('/librec-auto/metric/@optimize')[0])

                        command[1].execute(config, startflag = 1, exp_no = int(value_elems[0]))

                        bbo.file_path = file_path
                        bbo.create_space()
                        
                        bbo.run(int(value_elems[0]))

                        # print("continue_rerank", config.has_rerank())
                        # if config.has_rerank():
                        #     command[-3].execute(config)
                        #     # command[-2].execute(config)
                        #     command[-1].execute(config)
                        # else:
                        command[-1].execute(config)
                        create_study_output(config)



                 #   else:
                 #       print("Each range must have only two values!")
                 #       print("Expected", exponent_expected, "values, got", config.get_sub_exp_count())
                     
                else:
                    logging.error("Command instantiation failed.")
            else:
                logging.error("Configuration loading failed.")
        os.remove(librec_auto_log)
    
