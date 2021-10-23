============
Run a Study
============

Imagine you want to run a study with ``librec_auto``.

First, you will need to set up a configuration file. See the :ref:`Configuration file` documentation for information on the elements of a configuration file. Once your configuration file is complete, you can run your study.


Definitions
===========

What is an experiment?
----------------------

An experiment is a single job from the ``librec`` library.
This is what happens when you call the ``librec`` jar from the command line.

What is a study?
----------------

A study is a collection of experiments using the same algorithm the same data set, and the same methodology. ``librec_auto`` automates running
multiple experiments at once by varying algorithm hyperparameters, and the entity that encompasses a set of related
experiments is called a study. If you want to examine multiple algorithms or multiple data sets, you will need to define multiple studies.

Methodology
----------

The methodology in a ``librec-auto`` study includes information about how data is handled, what kinds of predictions are generated, and how they are evaluated. The methodology information is a bit distributed across the configuration file, and there are certain "gotchas" you should be aware of.

- As of LibRec 3.0, all cross-validation splits are drawn uniform-at-random from the ratings data set. The size of each split is N/k where N is the number of ratings and k is the number of splits. Other parameters (the style of split) that can be used in the single-split ``ratio`` model are ignored. 
- Ranking vs rating prediction methodology. If you are using a metric that looks at a ranked list of results (pretty much anything other than ``rmse``, ``mae`` and certain of the fairness metrics), you *must* specify the ranking element and the list-size element in the metric element in your configuration. See below. You will get very strange ranking results, if LibRec thinks you are using a rating prediction methodology.
- Ranking vs rating prediction algorithms. Some algorithms are optimized for ranking loss and the results that they produce may not be interpretable as prediction ratings for a user/item pair. For example, BPR, RankALS, or PLSA. These algorithms should only be used with the ranking element set and an appropriate ranking-type metric.  

::

	<ranking>true</ranking>
	<list-size>10</list-size>

Any list size can be used.	

File Structure
==============

Study Structure
---------------

``librec_auto`` has a specific project structure. If you want to run an study
named ``movies``, you will need to put your ``config.xml`` file in a ``conf``
directory inside a ``movies`` directory, like this:

::

    movies
    └── conf
        └── config.xml

You can then run your movies study with:

::

    $ python -m librec_auto run -t movies


This will update the ``movies`` directory to look like this:

::

    movies
    ├── conf
    │   └── config.xml
    ├── exp00000
    │   ├── conf
    │   │   ├── config.xml
    │   │   └── librec.properties
    │   ├── log
    │   │   └── librec-<timestamp>.log
    │   ├── original
    │   └── result
    │       ├── out-1.txt
    │       └── ...
    ├── exp00001
    │   ├── conf
    │   │   ├── config.xml
    │   │   └── librec.properties
    │   ├── log
    │   │   └── librec-<timestamp>.log
    │   ├── original
    │   └── result
    │       ├── out-1.txt
    │       └── ...
    ├── exp00002
    │   └── ...
    ├── exp00003
    │   └── ...
    └── ...
	output.xml

Each directory like ``exp00001`` represents one of the experiments from your
movies study. The number of ``exp#####`` directories is equal to the number of
permutations from the ``value`` items in your study-wide configuration file. The
``output.xml`` contains a summary of results over all the experiments and also a log of any warnings
or errors encountered.


Experiment Structure
--------------------

Let's consider a single experiment directory:

::

    exp00002
    ├── conf
    │   ├── config.xml
    │   └── librec.properties
    ├── log
    │   └── librec-<timestamp>.log
    ├── original
    └── result
        ├── out-1.txt
        ├── out-2.txt
        ├── out-3.txt
        ├── out-4.txt
        └── out-5.txt
	output.xml

* ``conf`` holds the auto-generated configuration file for this *experiment* (not for the study), as well as the ``librec.properties`` equivalent of the ``config.xml``.
    * Don't tamper with these files: to edit the experiment configurations, modify the study-wide ``movies/conf/config.xml`` file.
* ``log`` holds the log output from running the experiment. Many LibRec algorithms output log information containing training phase information and this can be found here.
* ``result`` holds the computed recommendation lists or predictions from the ``librec`` experiment.
* ``original`` is a directory used for experiments involving result re-ranking. The re-ranker will copy the original recommendation output from the algorithm to this directory. Re-ranked results are then place in the ``result`` directory so they can be located by subsequent processes. You can experiment with multiple hyperparameters for a re-ranking algorithm without recomputing the base recommendations. For example:
    * Re-rank the results with ``python -m librec_auto rerank movies``
* ``output.xml`` is a file that contains a summary of the experiment run. Metric results are stored here as well as any warnings or error messages encountered.