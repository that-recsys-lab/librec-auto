=============
Development
=============

Documentation
=============
..
  todo add details about read the docs

Documentation lives in ``librec_auto/docs/``, and is hosted on `Read the Docs`_.

.. _Read the Docs: https://librec-auto.readthedocs.io/en/latest/

To rebuild the docs:

#. ``cd librec_auto/docs/``
#. ``make clean && make html``.

Code Formatting
===============

..
  todo add yapf installation instructions

We use Yapf_ for python code formatting.
To format the whole codebase, run:

.. _Yapf: https://github.com/google/yapf

::

    yapf . -i --recursive

Docker
======
You can develop ``librec_auto`` in Docker.

The root-level Dockerfile only installs ``librec_auto``.
It does not actually run any experiments.
You can extend this file with your own code to further develop ``librec_auto``.

To use the Dockerfile, run the following in your bash terminal:

::

	docker build -t librec_auto:latest .
	docker run librec_auto:latest
