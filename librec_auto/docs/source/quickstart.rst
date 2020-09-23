=======================================
Quickstart guide
=======================================

Installation
============

You can install ``librec-auto`` using pip command as follows:

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

Get the following GitHub repository:

::

	https://github.com/that-recsys-lab/librec-auto-demo2020.git	

You can run a basic matrix factorization recommender over a movie ratings data set using the following command:

::
	$ python -m librec_auto -t _path_to_repository_/demo01 run

The configuration file that is followed to execute the study is found at the following path:

::
	_path_to_repository_/demo02/config/config.xml

The ``-c`` command line parameter allows other configuration files to be selected.
