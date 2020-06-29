# File structure

The standard file structure for a librec-auto experiment is as follows:

exp_home - this can be any directory. For example, one of the subdirectories of librec-auto-sample.

    / conf: Location for configuration files. Default "config.xml"

    / data: Location for data files (as per LibRec standard a directory with multiple data files is permitted)

        / split / cv_$i$: Location for the $i$th split of the data "train.txt" and "test.txt"

    / exp_$j$: Location for the $j$th sub-experiment (corresponding to a particular parameter configuration)

        .status: A file containing information about the sub-experiment

        / conf: Location for the properties file

        / result: Location for the results of the sub-experiment
        
        / original: If the results were re-ranked, the original results are moved here.

        / log: Location for log files from the sub-experiment

Note that we have changed the convention of having the experiments start at 1. Now they start at zero, which makes 
bookkeeping much easier.