================
Quickstart guide
================

Installation
============

You can install ``librec-auto`` using pip as follows:

::

	$ pip install librec-auto


Dependencies
------------
You will need to install the Java `Java Runtime Environment 8`_, since ``Librec`` is executed as a Java ``.jar``.

.. _Java Runtime Environment 8: https://java.com/en/download/

The installation is complete. You can now run your experiments with:

::

	$ python -m librec_auto


Building from Source
====================

Instead of installing ``librec_auto`` from pip, you can also build it from the source.

First, you'll need to clone this repository:

::

	$ git clone https://github.com/that-recsys-lab/librec-auto.git && cd librec-auto

Then, run the setup script:

::

	$ python setup.py install


If you already have ``librec_auto`` installed, you will need to uninstall
the ``librec_auto`` module before you install it from source. Run:

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

If your configuration file is set up to produce them, various compilations of the study results
will be stored in the ``target/post`` directory. You can also write your own post-processing scripts.
In this example, CSV output containing metric values have been stored. See the producing CSV output 
documentation for the configuration of this script and an explanation of its output.

One is the ``study-results-full`` file, which shows evaluation metrics for
every split from each experiment in the study.

The other is the ``study-results-summary`` file, which shows the average
evaluation metrics (across splits) for each experiment in the study.
