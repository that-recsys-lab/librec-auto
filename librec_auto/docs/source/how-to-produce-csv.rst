.. _SaveCSV:

===============================
Produce CSV Output
===============================
:Author:
		Robin Burke, Zijun Liu
:Version:
		Sep 7th, 2020

1. Introduction
===============

This post-processing script produces CSV summaries of the metrics computed for all of the experiments in a study. There are two types of output. 

* ``full`` output contains the value of the metric for each fold of the experiment. This option is only relevant for cross-validation studies.
* ``summary`` output contains the average value of the metric across all folds in an experiment or just the single value for studies that don't use cross-validation.

Files are stored in the ``post`` folder in the study directory. 


2. Configuration
================

1. In order to produce this output from your study, you will need to add a ``script`` element to the post-processing portion of the configuration file. Here is an example:

::

	<script lang="python3" src="system">
		<script-name>results_to_csv.py</script-name>
			<param name="option">all</param>
		</script> 
	</script>

2. ``option`` parameter

In addition to the ``full`` and ``summary`` options discussed above, there is also an ``all`` option that produces both kinds of output.

Files are named with the option and with a time stamp drawn from the log files that were processed. Example: ``study-results-summary_20200915_070451.csv``

