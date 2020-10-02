================
Quickstart guide
================

Installation
============

pip
---

You can install ``librec-auto`` using pip command as follows:

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
