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

You must be running Python 3.7+. (Run ``python --version`` to check your python version.)

Since ``librec-auto`` uses the ``Librec`` library for running the experiments,
you will need to also download the ``Librec`` library after installing ``librec-auto``.

You can use the helper ``install`` command from ``librec_auto``, like this:

::

	$ python -m librec_auto install

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
