============
Run a Study
============

Imagine you want to run a study with ``librec_auto``.
First, you will need to set up a configuration file. See the :ref:`Configuration file` documentation for information. Once your configuration file is complete, you can run your study.

Definitions
===========

What is an experiment?
----------------------

An experiment is a single job from the ``librec`` library.
This is what happens when you call the ``librec`` jar from the command line.

What is a study?
----------------

A study is a collection of experiments using the same algorithm and the same data set. ``librec_auto`` automates running
multiple experiments at once by varying algorithm hyperparameters, and the entity that encompasses a set of related
experiments is called a study. If you want to examine multiple algorithms, you will need to define multiple studies.

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

    $ python -m librec_auto run movies


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

Each directory like ``exp00001`` represents one of the experiments from your
movies study. The number of ``exp#####`` directories is equal to the number of
permutations from the ``value`` items in your study-wide ``config.xml``.


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

* ``conf`` holds the auto-generated configuration file for this *experiment* (not for the study), as well as the ``librec.properties`` equivalent of the ``config.xml``.
    * Don't tamper with these files: to edit the experiment configurations, modify the study-wide ``movies/conf/config.xml`` file.
* ``log`` holds the log output from running the experiment. Many LibRec algorithms output log information containing training phase information and this can be found here.
* ``result`` holds the computed recommendation lists or predictions from the ``librec`` experiment.
* ``original`` is a directory used for experiments involving result re-ranking. The re-ranker will copy the original recommendation output from the algorithm to this directory. Re-ranked results are then place in the ``result`` directory so they can be located by subsequent processes. You can experiment with multiple hyperparameters for a re-ranking algorithm without recomputing the base recommendations. For example:
    * Re-rank the results with ``python -m librec_auto rerank movies``