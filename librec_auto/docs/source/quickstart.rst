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
You will need to install the Java `Java Runtime Environment 8`_, since ``Librec`` is executed from a Java JAR file.

.. _Java Runtime Environment 8: https://java.com/en/download/

The installation is complete. You can now run your experiments with:

::

	$ python -m librec_auto -t <study directory>


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

Note on MS Recommenders
==================

The Microsoft Recommenders library is available as an installation extra: 

::

	$ pip install librec-auto[ms-recommend]
	
However, you may find it easier to install this package manually. In particular, pip will not install the library on version of
Python greater than 3.7. You also must have a version of tensorflow no later that 2.2.0. If you are installing on Python 3.8 or later,
we have had success installing from the GitHub repository directly.

::

	$ pip install -e git+https://github.com/microsoft/recommenders/#egg=pkg
	
The ``librec-auto-demo2021`` repository has a working example of using a variational autoencoder from MS Recommenders: `librec-auto-demo2021 <github.com/that-recsys-lab/librec-auto-demo2021>`_ 


Running an Example
==================

Clone the following ``librec-auto-demo2021`` repository:

::

	$ git clone https://github.com/that-recsys-lab/librec-auto-demo2021.git

You can run a basic matrix factorization recommender over a movie ratings data set using the following command:

::

	$ python -m librec_auto run -t librec-auto-demo2021/demo01 -c config01.xml

The configuration file for the above study is located at:

::

	$ librec-auto-demo2020/demo01/config/config01.xml

The ``-c`` command line parameter allows other configuration files to be selected.

Results
=======

Let's say you want to run a study in the target directory ``target``.

::

	target
	└── conf
	    └── config01.xml

Now, let's say you run the study, like:

::

	python -m librec_auto -t target run

Your directory structure should now look similar to this:

::

	target
	├── conf
	│   └── config01.xml
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
	output.xml

``librec-auto`` will run several experiments for your ``target`` study.
These experiments each have their own subdirectory, under ``target``. In the
diagram above, these subdirectories are like ``exp0000n``.

If your configuration file is set up to produce them, various compilations of the study results
will be stored in the ``target/post`` directory. You can also write your own post-processing scripts.

The ``output.xml`` file contains information about the run of the study including any errors or warning that were encountered.

Quickstart with your own data
========

To quickly set up a librec-auto study using your own data, you can use the setup wizard provided. This is a python script located in the ``librec-auto/bin`` folder. Run the wizard with the following arguments

::

    $ python path_to_librec-auto/bin/wizard.py --data your_data_file --study path_of_study_directory

The wizard will create a study file structure as described above and import your data file into it. It will also create a configuration with a basic experimental setup. You can run the study with the following commands:

::

    $ cd path_of_study_directory
    $ python -m librec_auto run -t .

Your results will be stored in the ``output.xml`` file in the study directory.

