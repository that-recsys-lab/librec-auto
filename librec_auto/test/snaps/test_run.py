from pathlib import Path
import shutil
import io
import os

import librec_auto.__main__ as main


def test_run(capsys, ):
    # make directories
    run_directory = Path('librec_auto/test/snaps/run')
    run_directory.mkdir(exist_ok=True)
    Path('librec_auto/test/snaps/run/conf').mkdir(exist_ok=True)

    # move config file to 'test_run/conf/config.xml'
    current_config = Path('librec_auto/test/snaps/config.xml')
    new_config = Path('librec_auto/test/snaps/run/conf/config.xml')
    shutil.copy(current_config, new_config)

    # run command
    args = {
        'action': 'run',
        'target': 'librec_auto/test/snaps/run',
        'conf': None,
        'dry_run': False,
        'quiet': True,
        'no_parallel': False,
        'purge': 'all',
        'no_cache': False,
        'dev': False,
        'HT': False,
        'PCO': False,
        'int': False,
        'key_password': None
    }
    config = main.load_config(args)
    command = main.setup_commands(args, config)
    command.execute(config)

    post_directory = Path('librec_auto/test/snaps/run/post')
    post_files = os.listdir(post_directory)

    results_full = [
        f for f in post_files if f.startswith('study-results-full')
    ][0]
    results_summary = [
        f for f in post_files if f.startswith('study-results-summary')
    ][0]

    # test full results
    assert file_equal_to_string(post_directory / results_full,
                                get_study_results_full())

    # test summary results
    assert file_equal_to_string(post_directory / results_summary,
                                get_study_results_summary())

    # test librec.properties generation
    assert file_equal_to_string(
        run_directory / Path('exp00000/conf/librec.properties'),
        get_exp00000_librec_properties())

    # remove the run dir
    shutil.rmtree(Path('librec_auto/test/snaps/run'))


def file_equal_to_string(file_path, check_string):
    with open(file_path, 'r') as file:
        data = file.read()
        return data == check_string


def get_study_results_full():
    return """Experiment,Split,item-reg,NormalizedDCG,Precision
exp00000,0,0.001,0.10208332844114967,0.09383791024782248
exp00000,1,0.001,0.09932512239867436,0.09460997656511488
exp00000,2,0.001,0.08963159563388595,0.08371237458193871
exp00001,0,0.01,0.08333869173650575,0.08258539852645559
exp00001,1,0.01,0.07999419745417015,0.0809507867425499
exp00001,2,0.01,0.06656193661353892,0.06638795986621991
exp00002,0,0.05,0.06189981061058677,0.06577361018084282
exp00002,1,0.05,0.0521462428377912,0.05363240709742148
exp00002,2,0.05,0.044975566799949705,0.048260869565216816
"""


def get_study_results_summary():
    return """Experiment,item-reg,NormalizedDCG,Precision
exp00000,0.001,0.09701334882456998,0.09072008713162537
exp00001,0.01,0.07663160860140494,0.0766413817117418
exp00002,0.05,0.05300720674944256,0.05588896228116038
"""


def get_exp00000_librec_properties():
    return """dfs.result.dir: exp00000/result
dfs.log.dir: log
dfs.split.dir: split
rec.random.seed: 202001
rec.thread.count: 1
dfs.data.dir: ../data
data.column.format: UIR
data.input.path: ratings.csv
data.model.format: text
data.model.splitter: kcv
data.splitter.cv.number: 3
data.splitter.ratio: userfixed
data.splitter.trainset.ratio: 0.8
data.splitter.save: true
rec.recommender.class: biasedmf
rec.iterator.learnrate: 0.01
rec.iterator.learnrate.maximum: 0.01
rec.learnrate.decay: 1.0
rec.learnrate.bolddriver: false
rec.iterator.maximum: 25
rec.user.regularization: 0.01
rec.item.regularization: 0.001
rec.bias.regularization: 0.01
rec.factor.number: 20
rec.recommender.earlystop: true
rec.similarity.class: pcc
rec.recommender.similarities: item
rec.recommender.isranking: true
rec.recommender.ranking.topn: 10
rec.eval.classes: ndcg,precision
"""
