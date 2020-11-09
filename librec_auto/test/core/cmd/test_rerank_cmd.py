from pathlib import Path
from shutil import copyfile, rmtree

import sys

from librec_auto.core.cmd.rerank_cmd import RerankCmd
from librec_auto.core import ConfigCmd

RERANK_DIR = 'librec_auto/test/core/cmd/rerank'


def test_run_script():
    sys.argv = ['-t', RERANK_DIR]
    # create file structure

    # mkdir rerank
    rerank_path = Path(RERANK_DIR)
    rerank_path.mkdir(exist_ok=True)

    # make study conf directory
    study_conf_path = (rerank_path / Path('conf'))
    study_conf_path.mkdir(exist_ok=True)

    # copy study config
    copyfile(
        Path('librec_auto/test/data/rerank-utils/rerank-study-config.xml'),
        study_conf_path / 'config.xml')

    # make experiment directory
    experiment_path = (rerank_path / Path('exp00000'))
    experiment_path.mkdir(exist_ok=True)

    # make original directory
    original_path = (experiment_path / Path('original'))
    original_path.mkdir(exist_ok=True)

    # make experiment conf directory
    experiment_conf_path = (experiment_path / Path('conf'))
    experiment_conf_path.mkdir(exist_ok=True)

    # copy experiment config
    copyfile(
        Path(
            'librec_auto/test/data/rerank-utils/rerank-experiment-config.xml'),
        experiment_conf_path / 'config.xml')

    (experiment_path / Path('results')).mkdir(exist_ok=True)

    # copy out-1.txt and out-2.txt to original
    copyfile(Path('librec_auto/test/data/rerank-utils/original-out-1.txt'),
             original_path / 'out-1.txt')
    copyfile(Path('librec_auto/test/data/rerank-utils/original-out-2.txt'),
             original_path / 'out-2.txt')

    # create RerankCmd
    config = ConfigCmd(RERANK_DIR + '/conf/config.xml', RERANK_DIR)

    rerank = RerankCmd()

    script = Path('../../../../../librec_auto/core/cmd/rerank/far_rerank.py')
    param_spec = ['--max_len=4', '--lambda=0.3', '--binary=False']

    rerank._files = config.get_files()

    rerank._files.create_exp_paths(0)  # create experiment tuple

    sub_paths = rerank._files.get_exp_paths(0)

    rerank._config = config  # set config

    result = rerank.run_script(script=script,
                               sub_paths=sub_paths,
                               original_path=original_path,
                               param_spec=param_spec)

    assert result == 0

    # todo verify the reranking worked here

    rmtree(RERANK_DIR)  # delete the reranking directory

    assert 1 == 0  # display results

    # import pdb
    # pdb.set_trace()
