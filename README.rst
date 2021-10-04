============
Librec-auto
============


.. image:: https://coveralls.io/repos/github/that-recsys-lab/librec-auto/badge.svg?branch=master
  :target: https://coveralls.io/github/that-recsys-lab/librec-auto?branch=master

About
=====

``librec-auto`` is a Python tool for running recommender systems experiments.
It is built on top of the open-source LibRec_ package, and
can take advantage of the many algorithm and metric implementations there.

.. _LibRec: https://github.com/guoguibing/librec

The basic element of ``librec-auto`` execution is the "study", which is a series
of experiments carried with a single algorithm, a single data set, and a set
of evaluation metrics. The experiments differ from each other by the hyperparameters
given to the algorithm. ``librec-auto`` allows such studies to be conducted with
minimal experimenter intervention, and supports such capabilities as:

* recommendation result re-ranking
* re-running evaluations without re-computing results
* summarizing results in output graphs
* integration with Slack and Dropbox

More complete documentation is available at readthedocs_:

.. _readthedocs: https://librec-auto.readthedocs.io/en/latest/index.html

Workflow
========

The workflow of an study involves identifying appropriate data, creating
training / test splits, implementing or choosing algorithms, running experiments
(possibly with a range of different parameters), and reporting on the results.

Configuration
=============

Librec-auto uses an XML-based configuration system similar to Maven or Ant.

Project structure
=================

This directory contains the Python libraries for the librec_auto module. There are two other affiliated
respositories:

* `librec-auto-java`_: Contains the java source for the wrapper between LibRec and librec-auto, which is implemented in the ``auto.jar`` file.
* `librec-auto-sample`_: Contains sample data and configuration files that can be used to explore the functionality of librec-auto

.. _librec-auto-java: https://github.com/that-recsys-lab/librec-auto-java
.. _librec-auto-sample: https://github.com/that-recsys-lab/librec-auto-sample

Repo structure
===============

* ``/jar``: Contains the jar files for LibRec and the wrapper.
* ``/rules``: Contains the rules for translating configuration data to LibRec properties format.
* ``/librec_auto``: Contains the Python code for the project.
* ``/doc``: Contains documentation for the project
* ``/test``: Contains the unit tests (not many right now)
