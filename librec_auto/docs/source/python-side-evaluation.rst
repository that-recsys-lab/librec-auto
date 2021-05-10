======================
Python-side Evaluation
======================


Existing Metrics
================

To use existing python-side metrics, use the ``python="true"`` flag in your
configuration file's metrics:

::

	<metric python="true">
		<name>rmse</name>
	</metric>

Custom Metrics
==============

``librec-auto`` supports custom evaluation metrics implemented in python.

Adding a row-based metric (i.e., RMSE)
--------------------------------------

For metrics that are based solely upon an item's expected and actual results
(and not the entire lists' results), ``librec-auto`` provides the ``RowBasedMetric``
superclass.

1. Create the new class file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, make a file in the ``librec_auto/core/eval/metrics`` directory. Name the file
``<metric_name>_metric.py``, like ``rmse_metric.py``.

2. Override the ``RowBasedMetric`` methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``__init__``
""""""""""""

Override ``__init__`` and set ``self._name`` equal to the name of the metric.
Do not forget to call ``super().__init__``.

::

	def __init__(self, params: dict, test_data: np.array,
	             result_data: np.array) -> None:
	    super().__init__(params, test_data, result_data)
	    self._name = 'RMSE'

``evaluate_row``
""""""""""""""""

This method performs the actual evaluation of the results. The first parameter contains
the test (expected) values for the item,user combination. The second
parameter contains the actual values for the item,user combination. Both are numpy
arrays, and should be indexed to access the row values. This method should
return the value of the metric for the given user,item combination.

``evaluate_row`` for RMSE using ``librec-auto`` Python-side Evaluation:

::

	def evaluate_row(self, test: np.array, result: np.array):
	    test_ranking = test[2]
	    result_ranking = result[2]
	    return (test_ranking - result_ranking)**2

``pre_row_processing`` and ``post_row_processing``
""""""""""""""""""""""""""""""""""""""""""""""""""

The ``pre_row_processing`` method allows for setting initial values or other
processing that should be performed before any of the rows are processed.
Think of this like setting up the metric.

The ``post_row_processing`` method is passed an array of values, and returns
a single value that represents the final value of the metric.

The array of values is an array created from the results of the ``evaluate_row``
method.

``post_row_processing`` for RMSE using ``librec-auto`` Python-side Evaluation:

::

	def post_row_processing(self, values):
	    T = len(values)
	    return (sum(values) / T)**0.5


todo add info to update mapping dict

Adding a list-based metric (i.e., NDCG)
---------------------------------------

For metrics that require the entire result list for computation, ``librec-auto``
provides the ``ListBasedMetric`` superclass, which can be inherited by custom class
metrics.
