#! venv/bin/python
import argparse
import subprocess
from pathlib2 import Path
import datetime
from . import utils
import shutil
import itertools
import os
import glob
from .exp_paths import ExpPaths
from .log_file import LogFile
from .config_simple import ConfigSimple
import threading




EXP_DIR_PATTERN = "exp{:03d}"

def get_experiment_paths(count, path, create=False):
    dir_name = EXP_DIR_PATTERN.format(count)
    return ExpPaths(path, dir_name, create=create)

def save_properties(prop_dict, path):
    with path.open(mode="w") as fh:
        fh.write(u'# DO NOT EDIT\n# Properties file created by librec-auto\n')
        # for key, value in prop_dict.iteritems():
        for key, value in prop_dict.items():
            line = "{}:{}\n".format(key, value)  # type: str
            # fh.write(unicode(line))
            fh.write(str(line))

status_header = '<?xml version="1.0"?>\n<!-- DO NOT EDIT. File automatically generated by librec-auto -->\n'

status_template_front = '<librec-auto-status>\n<message>{}</message>\n<exp-no>{}</exp-no>\n<date>{}</date>\n'

status_template_param = '<param><name>{}</name><value>{}</value></param>\n'

status_end = '</librec-auto-status>\n'

# Accept list of vars and tuples
def save_status(msg, exp_count, var_names, value_tuple, config, paths):
    status_file = paths.get_path('status')
    status_front = status_template_front.format(msg, exp_count, datetime.datetime.now())

    status_params = ''

    for var, val in zip(var_names, value_tuple):
        status_params = status_params + status_template_param.format(var, val)

    status_info = status_header + status_front + status_params + status_end

    with status_file.open(mode='w') as fh:
        fh.write(str(status_info))
        # fh.write(unicode(status_info))

# LibRec is very stubborn about the location of the log
LOG_PATH = "../log/librec.log"
def copy_log(log_path):
    default_log_path = Path(LOG_PATH)
    dest_path = log_path / "librec.log"
    shutil.copy(str(default_log_path), str(dest_path))

DEFAULT_CONFIG_FILENAME = "config.xml"

# 2018-06-28 RB
# This is the 2018-07-01 demo option
def run(target, command, config_path):
    print("1")
    base_path = Path(target)
    print("2")
    print ("librec-auto: Running experiments in ", target)

    print("3")
    config_filepath = base_path / config_path / DEFAULT_CONFIG_FILENAME
    print("4")
    if not config_filepath.is_file():
        print("librec-auto: Configuration file {} not found. Exiting".format(str(config_path)))
        exit(-1)

    print("5")
    config = ConfigSimple(config_path)
    print("6")
    config.convert_properties()
    config_out = config.get_prop_dict()
    # This is kind of a hack
    config_out['dfs.split.dir'] = "split"
    var_data = config.get_var_data()
    exp_count = 1

    var_params = var_data.keys()
    _var_values = var_data.values()
    var_values = []
    for element in _var_values:
        if type(element) is list:
            # print(element)
            var_values.append(element)
        else:
            var_values.append([element])
    if len(var_values) == 1:
        value_tuples = [var_values]
    else:
        value_tuples = list(itertools.product(*var_values))
    flag_val = 0
    # ts = [None] * len(value_tuples)

    print("7")
    thread_count = int(config_out['rec.thread.count'])
    threads = []
    j = 0
    while(j < len(value_tuples)):  # Iteerate over configurations of variable values
        for k in range(thread_count):
            if(j < len(value_tuples)):
                value_tuple = value_tuples[j]
                thread = threading.Thread(name="thread"+str(k),target=execute_librec_thread, args = (exp_count, base_path,var_params,value_tuple,config_out.copy(),config,command, ))
                threads.append(thread)
                thread.start()
                exp_count += 1
                j += 1
        # # flag_val = execute_librec_thread(exp_count, base_path,var_params,value_tuple,config_out,config,command)
        for thread in threads:
            thread.join()


    print("librec-auto: Experiments in ", target, " completed.")

    if (config.get_post_script() is not None) and (flag_val != 0):
        print("librec-auto: Post processing for", target)

        viz(target, config)

        print("librec-auto: Post processing complete")


def execute_librec(path, command):
    classpath = "../lib/auto/out/artifacts/auto_jar/auto.jar"
    mainClass = "net.that_recsys_lab.auto.SingleJobRunner"
    confpath = path / "conf/librec.properties"
    logpath = path / "log/librec.log"

    java_command = setup_env(path, command)
    print("10")
    if (java_command is not None):
        cmd = ['java', '-cp', classpath, mainClass, str(confpath), java_command]
        f = open(str(logpath), 'w+')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout:
            # f.write(line)
            f.write(str(line))
    print ("11")

def execute_librec_thread(exp_count, base_path,var_params,value_tuple,config_out,config,command):
    print ("8")
    paths = get_experiment_paths(exp_count, base_path, create=True)
    exp_path = paths.get_path('exp')
    for key, value in zip(var_params, value_tuple):
        config_out[key] = value  # Loop over all variables, value pairs
    paths.add_to_config(config_out, 'result')
    save_properties(config_out, exp_path / "conf/librec.properties")
    # Pass list of vars and tuple
    save_status("Executing", exp_count, var_params, value_tuple, config, paths)
    # log file appends by default

#        os.unlink(LOG_PATH)
    # Try block might be better?
    librec_log = Path(LOG_PATH)
    if librec_log.is_file():
        librec_log.unlink()

    print("9")
    execute_librec(exp_path, command)
    print ("12")
    save_status("Completed", exp_count, var_params, value_tuple, config, paths)

    # Aldo's fault - This is only because if we 'split' something with splits made already, it will throw and error
    flag_val = 0
    try:
        # copy_log(paths.get_path('log'))
        flag_val = flag_val+1
    except:
        pass

    return flag_val

def setup_env(path, command):
    path_str = str(path)
    expVal = path_str[-3:]
    
    if (command == 'split'):
        # check if split exists
        cv_path = path_str[:4]+'/data/split/cv_'+str(int(expVal))+'/train.txt'
        cv_path = Path(cv_path)
        if(cv_path.is_file()):
            print("Split already exists. Skipping.")
            return None
        else:
            return 'split'
    
    if (command == 'eval'):
        # first check if results exist
        res_path = path.as_posix()+'/result/out-1.txt'
        # print('res path '+res_path)
        res_path = Path(res_path)
        if(res_path.is_file()):
            print ("eval - running reRunEval")
            return 'reRunEval'
        else: # No result file present, Then check if split exists
            cv_path = path_str[:4]+'/data/split/cv_'+str(int(expVal))+'/train.txt'
            cv_path = Path(cv_path)
            if(cv_path.is_file()):
                print ("eval - running exp-eval")
                return 'exp-eval'
            else:
                print ("eval - running full")
                return 'full'
    
    if (command == 'full'):
        return 'full'

    if (command == 'post'):
        return None                 # No Java execution needed

    
# <librec-auto-status>
#    <message>Completed</message>
#    <exp-no>1</exp-no>\
#    <param><name>rec.neighbors.knn.number</name><value>30</value></param>
#    <date>June 28, 11:00 PM</date>
# </librec-auto-status>
def print_status(exp_path):
    try:
        status_dict = utils.xml_load_from_path(exp_path)['librec-auto-status']
        print ("Experiment", status_dict['exp-no'], ": ", status_dict['message'], " at ", status_dict['date'])
        for param in utils.force_list(status_dict['param']):
            print ("   ", param['name'], ":", param['value'])
    except:
        print ("Error reading status for" + exp_path)


def print_log_info(paths):
    log = LogFile(paths)
    kcv_count = log.get_kcv_count()
    if kcv_count is None:
        print_metric_info(log, 1)
    else:
        # Print averages first
        print_metric_info(log, -1)
        # for i in range(0, int(kcv_count)):
        #     print "    Fold ", i+1
        #     print_metric_info(log, i)

def print_metric_info(log, idx):
    for metric_name in log.get_metrics():
        metric_value = log.get_metric_values(metric_name)[idx]
        print ("    {}: {:.4f}".format(metric_name, float(metric_value)))

def status(target):
    base_path = Path(target)
    exp_count = 1
    last_exp = False
    print ("librec-auto: Experiment status for", target)
    while (not last_exp):
        paths = get_experiment_paths(exp_count, base_path, create=False)
        status_path = paths.get_path('status')
        if status_path.exists():
            print_status(status_path)
            print_log_info(paths)
            exp_count += 1
        else:
            last_exp = True

    # No experiments
    if exp_count == 1:
        print ("librec-auto: No experiments found.")

def purge_confirm(target):
    prompt_str = "This will delete all experiments and/or file splits in directory {}".format(target)
    return utils.confirm(prompt=prompt_str, resp=False)

def purge_experiments(target,base_path,exp_count,last_exp):
    print ("librec-auto: Purging experiments ", target)
    while (not last_exp):
        paths = get_experiment_paths(exp_count, base_path, create=False)

        exp_path = paths.get_path('exp')
        if exp_path.exists():
            exp_str = paths.get_path_str('exp')
            print ("Deleting experiment directory: ", exp_str)
            shutil.rmtree(exp_str)
        else:
            last_exp = True
        exp_count += 1
    if(last_exp and exp_count==2):
        print ("librec-auto: No experiments folders found in ", target)
    else:
        print ("librec-auto: Experiments purged in ", target)

def purge_splits(target, base_path, exp_count, last_exp):
    # This is kind of a hack since it doesn't check that actual values of the data directory etc in the
    # configuration file.
    split_path = base_path / "data" / "split"
    if split_path.exists():
        print ("librec-auto: Deleting split directories ", target)
        shutil.rmtree(split_path.as_posix())
    else:
        print ("librec-auto: No split directories found in", target)


def purge_post(target, base_path):
    viz_path = base_path / "viz"

    if viz_path.exists():
        print ("librec-auto: Deleting viz directory files ", target)

        files = viz_path.glob('*')
        for f in files:
            os.remove(str(f))
    else:
        print ("librec-auto: viz directory missing ", target)

def purge(target, purgetype):

    base_path = Path(target)
    exp_count = 1
    last_exp = False
    #print "librec-auto: Purging experiments ", target
    if purge_confirm(target):
        if (purgetype == "all"):
            purge_experiments(target, base_path, exp_count, last_exp)
            purge_splits(target, base_path, exp_count, last_exp)

        if (purgetype == "results"):
            purge_experiments(target, base_path, exp_count, last_exp)

        if (purgetype == "split"):
            purge_splits(target, base_path, exp_count, last_exp)

        if (purgetype == "post"):
            purge_post(target, base_path)
    else:
        print ("librec-auto: Skipping. No files deleted.")

def viz(target, config):

    viz_path = Path(target) / 'viz'

    if not viz_path.exists():
        print ('librec-auto: viz directory missing. Creating. ', target)
        os.makedirs(str(viz_path))

    python_path = Path('venv/bin/python')
    win_python_path = Path('venv/Scripts/python.exe')  # Very annoying that I have to do this

    if python_path.is_file():
        cmd = [python_path.as_posix(), config.get_post_script(), target]
        subprocess.call(cmd)
    elif win_python_path.is_file():
        cmd = [str(win_python_path.as_posix()), config.get_post_script(), target]
        subprocess.call(cmd)
    else:
        print ("Python virtual environment not available at venv. Please install to use this function.")

# -------------------------------------


if __name__ == '__main__':
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
    dictargs = vars(args)

    config_file =  DEFAULT_CONFIG_FILENAME

    if 'conf' in dictargs:      # User requested a different configuration file
        config_file = dictargs['conf']

    if dictargs['Actions'] == 'run':    # Runs 'full' on the java side. Checker needs to see if any or all steps are made yet.
        purge(dictargs['target'], 'all')
        run(dictargs['target'], 'full', config_file)

    if dictargs['Actions'] == 'split':  # Runs 'split' on the java side.  Checker needs to see if split data already exists.
        run(dictargs['target'], 'split', config_file)

    if dictargs['Actions'] == 'eval':  # Runs 'eval' on the java side.  Checker needs to ...
        run(dictargs['target'], 'eval', config_file)

    if dictargs['Actions'] == 'post':  # Runs 'post' on the python side.
        a=1 # place holder

    if dictargs['Actions'] == 'purge':

        purgetype = "all"

        if args.split:
            purgetype = "split"
        if args.results:
            purgetype ="results"
        if args.post:
            purgetype = "post"

        purge(dictargs['target'], purgetype)

    if dictargs['Actions'] == 'reset':
        reset()

    if dictargs['Actions'] == 'status':
        status(dictargs['target'])
