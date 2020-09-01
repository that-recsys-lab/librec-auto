=============
Development
=============

Documentation
================
..
  todo add details about read the docs

Documentation lives in ``librec_auto/docs/``, and is hosted on `Read the Docs`_.

.. _Read the Docs: https://librec-auto.readthedocs.io/en/latest/

To rebuild the docs:

#. ``cd librec_auto/docs/``
#. ``make clean && make html``.

Code Formatting
================

..
  todo add yapf installation instructions

We use Yapf_ for python code formatting.
To format the whole codebase, run:

.. _Yapf: https://github.com/google/yapf

::

    yapf . -i --recursive
