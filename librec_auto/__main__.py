import argparse
from pathlib import Path

from librec_auto import ConfigCmd
from librec_auto.util import Files
from librec_auto.cmd import Cmd, SequenceCmd, PurgeCmd, LibrecCmd, PostCmd, RerankCmd, StatusCmd, ParallelCmd
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
    parser.add_argument("-dr","--dry_run", help = "stub",action ="store_true")
    parser.add_argument("-q","--quiet", help = "stub",action ="store_true")
    parser.add_argument("-np","--no_parallel", help = "stub",action ="store_true")

    parser.add_argument("-s", "--split", help="stub", action="store_true")
    parser.add_argument("-r", "--results", help="stub", action="store_true")
    parser.add_argument("-p", "--post", help="stub", action="store_true")

    args = parser.parse_args()
    return vars(args)


def read_config_file(args):

    config_file =  Files.DEFAULT_CONFIG_FILENAME

    if args['conf']:      # User requested a different configuration file
        config_file = args['conf']

    files = Files()

    #files.set_global_path(Path(__file__).parent.absolute())
    files.set_exp_path(args['target'])
    files.set_config_file(config_file)

    config = ConfigCmd(files)
    config.process_config()
    return config


def purge_type (args):
    if args.split:
        return "split"
    if args.results:
        return "results"
    if args.post:
        return "post"


def build_librec_commands(librec_action, config):
    librec_commands = [LibrecCmd(librec_action, i) for i in range(config.get_sub_exp_count())]
    threads = 1
    if 'rec.thread.count' in config.get_prop_dict():
        threads = int(config.get_prop_dict()['rec.thread.count'])

    if threads > 1:
        return ParallelCmd(librec_commands, threads)
    else:
        return SequenceCmd(librec_commands)


def setup_commands (args, config):
    action = args['Actions']
    purge_noask = args['quiet']

    rerank_flag = False
    if config.get_unparsed('rerank') is not None:
        rerank_flag = True

    post_flag = False
    if config.get_unparsed('post') is not None:
        post_flag = True

    # Purge files (possibly) from splits and subexperiments
    if action == 'purge':
        cmd = PurgeCmd(purge_type(args), noask=purge_noask)
        return cmd

    # Shows the status of the experiment
    if action == 'status':
        cmd = StatusCmd()
        return cmd

    # Perform (only) post-processing on results
    if action == 'post' and post_flag:
        cmd = PostCmd()
        return cmd
    # No re-ranker available
    if action == 'post' and not post_flag:
        logging.warning("No post-processing scripts available for post command.")
        return None

    # Perform re-ranking on results, followed by post-processing
    if action == 'rerank' and rerank_flag: # Runs a reranking script on the python side
        cmd1 = PurgeCmd('rerank', noask=purge_noask)
        cmd2 = RerankCmd()
        cmd = SequenceCmd([cmd1, cmd2])
        if post_flag:
            cmd.add_command(PostCmd())
        return cmd
    # No re-ranker available
    if action == 'rerank' and not rerank_flag:
        logging.warning("No re-ranker available for re-rank command.")
        return None

    # LibRec actions
    # re-run splits only
    if action == 'split':
        cmd1 = PurgeCmd('split', noask=purge_noask)
        cmd2 = build_librec_commands('split', config)
        cmd = SequenceCmd([cmd1, cmd2])
        return cmd

    # eval-only
    if action == 'eval':
        cmd1 = PurgeCmd('post', noask=purge_noask)
        cmd2 = build_librec_commands('eval', config)
        cmd = SequenceCmd([cmd1, cmd2])
        if post_flag:
            cmd.add_command(PostCmd())
        return cmd

    # run experiment and evals
    if action == 'run':
        cmd1 = PurgeCmd('results', noask=purge_noask)
        cmd2 = build_librec_commands('full', config)
        cmd = SequenceCmd([cmd1, cmd2])
        if rerank_flag:
            cmd.add_command(RerankCmd())
        if post_flag:
            cmd.add_command(PostCmd())

        return cmd

# -------------------------------------


if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args)

    if len(config.get_prop_dict()) > 0:
        command = setup_commands(args, config)
        if isinstance(command, Cmd):
            if args['dry_run']:
                command.dry_run(config)
            else:
                command.execute(config)
        else:
            logging.error("Command instantiation failed.")
    else:
        logging.error("Configuration loading failed.")
