================
Quickstart guide
================

Installation
============

You can install ``librec-auto`` using pip as follows:

::

	$ pip install librec-auto

You can now run your experiments using ``librec-auto``.

Building from Source
====================

Instead of installing ``librec_auto`` from pip, you can also build it from the source with:

::

	$ python setup.py install

You may need to uninstall the ``librec_auto`` module first, by running:

::

	$ pip uninstall librec_auto

Running an Example
==================

Clone the following ``librec-auto-demo2020`` repository:

::

	$ git clone https://github.com/that-recsys-lab/librec-auto-demo2020.git

You can run a basic matrix factorization recommender over a movie ratings data set using the following command:

::

	$ python -m librec_auto -t librec-auto-demo2020/demo01 run

The configuration file for the above study is located at:

::

	$ librec-auto-demo2020/demo01/config/config.xml

The ``-c`` command line parameter allows other configuration files to be selected.

Results
=======

Let's say you want to run a study in the target directory ``target``.

::

	target
	└── conf
	    └── config.xml

Now, let's say you run the study, like:

::

	python -m librec_auto -t target run

Your directory structure should now look similar to this:

::

	target
	├── conf
	│   └── config.xml
	├── exp00000
	│   ├── conf
	│   │   ├── config.xml
	│   │   └── librec.properties
	│   ├── log
	│   │   └── librec-<timstamp>.log
	│   ├── original
	│   └── result
	│       ├── out-1.txt
	│       ├── out-2.txt
	│       └── ...
	├── exp00001
	│   └── ...
	├── exp00002
	│   └── ...
	├── ...
	└── post
	    ├── study-results-full_<timestamp>.csv
	    ├── study-results-summary_<timestamp>.csv
	    └── ...

``librec-auto`` will run several experiments for your ``target`` study.
These experiments each have their own subdirectory, under ``target``. In the
diagram above, these subdirectories are like ``exp0000n``.

At the study level, two results files are generated in the ``target/post``
directory.

One is the ``study-results-full`` file, which shows evaluation metrics for
every split from each experiment in the study.

The other is the ``study-results-summary`` file, which shows the average
evaluation metrics (across splits) for each experiment in the study.

The columns are almost the same for both files. The first column (column A) is
always the experiment name (like ``exp0000n``, zero indexed). The second column
(column B) in ``study-results-full`` *only* (*not* in
``study-results-summary``) is the split number for the experiment (zero indexed).

The following columns (B and onward for ``study-results-summary``, C and onward
for ``study-results-full``) are the evaluation metrics, which are specific to
the algorithm chosen for the study.
