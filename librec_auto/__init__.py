#! venv/bin/python
import argparse
from pathlib import Path
from librec_auto.util import utils
from librec_auto.util.sub_paths import SubPaths
from librec_auto.util.log_file import LogFile
from librec_auto.cmd import Cmd, SequenceCmd, PurgeCmd, LibrecCmd, PostCmd, RerankCmd, StatusCmd, ParallelCmd
from .config_cmd import ConfigCmd
import logging


def read_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('Actions',choices=['run','split', 'eval', 'post', 'purge', 'status']) # deleted exp

    parser.add_argument("target", help="what the action applies to")

    # Optional with arguments
    # parser.add_argument("-ex","--exhome", help="stub")
    # parser.add_argument("-rs","--reset", help = "stub")
    # parser.add_argument("-rss","--revise-step", help="stub")
    parser.add_argument("-c", "--conf", help="stub")

    # Flags
    parser.add_argument("-nc","--no_cache", help = "stub",action ="store_true")
    parser.add_argument("-do","--display_only", help = "stub",action ="store_true")
    parser.add_argument("-q","--quiet", help = "stub",action ="store_true")
    parser.add_argument("-np","--no_parallel", help = "stub",action ="store_true")

    parser.add_argument("-s", "--split", help="stub", action="store_true")
    parser.add_argument("-r", "--results", help="stub", action="store_true")
    parser.add_argument("-p", "--post", help="stub", action="store_true")

    args = parser.parse_args()
    return vars(args)


def read_config_file(args):

    config_file =  DEFAULT_CONFIG_FILENAME

    if 'conf' in args:      # User requested a different configuration file
        config_file = args['conf']

    files = Files()

    files.set_global_path(Path(__file__).parent.absolute)
    files.set_exp_path(args[target])
    files.set_config_file(config_file)

    config = ConfigCmd(files)
    config.process_config()


def purge_type (args):
    if args.split:
        return "split"
    if args.results:
        return "results"
    if args.post:
        return "post"


def build_librec_commands(librec_action, config):
    librec_commands = [LibrecCmd(librec_action, i) for i in range(1, config.files.get_sub_count()+1)]
    threads = int(config.get_prop_dict()['rec.thread.count'])

    if threads > 1:
        return ParallelCmd(librec_commands, threads)
    else:
        return SequenceCmd(librec_commands)


def setup_commands (args, config):
    action = args['Actions']
    # Purge files (possibly) from splits and subexperiments
    if action == 'purge':
        cmd = PurgeCmd(purge_type(args))
        return cmd
    # Perform (only) post-processing on results
    if action == 'post':
        cmd = PostCmd()
        return cmd
    # Perform re-ranking on results, followed by post-processing
    if action == 'rerank': # Runs a reranking script on the python side
        cmd1 = PurgeCmd('rerank')
        cmd2 = RerankCmd()
        cmd3 = PostCmd()
        cmd = SequenceCmd([cmd1, cmd2, cmd3])
        return cmd
    # Shows the status of the experiment
    if action == 'status':
        cmd = StatusCmd()
        return cmd
    # LibRec actions
    # eval-only
    if action == 'eval':
        cmd1 = PurgeCmd('post')
        cmd2 = LibrecCmd('eval')
        cmd = SequenceCmd([cmd1, cmd2])
        return cmd
    # run experiment only
    if action == 'run':
        cmd1 = PurgeCmd('results')
        cmd2 = LibrecCmd('run')
        cmd3 = RerankCmd()
        cmd4 = PostCmd()
        cmd = SequenceCmd([cmd1, cmd2, cmd3, cmd4])
        return cmd
    # re-run splits only
    if action == 'split':
        cmd1 = PurgeCmd('split')
        cmd2 = LibrecCmd('split')
        cmd = SequenceCmd([cmd1, cmd2])
        return cmd

# -------------------------------------

if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args)

    if len(config.get_prop_dict()>0):
        command = setup_commands(args, config)
        if (type(command) is Cmd):
            command.execute()
        else:
            logging.error("Command instantiation failed.")
    else:
        logging.error("Configuration failed.")
