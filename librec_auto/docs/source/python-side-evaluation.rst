======================
Python-side Evaluation
======================


Existing Metrics
================

To use existing python-side metrics, use the ``python="true"`` flag in your
configuration file's metrics. The ``params`` element shown here can be empty.

::

	<metric python="true">
		<name>rmse</name>
		<params>
			<foo>bar</foo>
		</params>
	</metric>

Custom Metrics
==============

``librec-auto`` supports custom evaluation metrics implemented in python.


Required boilerplate
--------------------

Regardless of the type of metric you're implementing, you will need some boilerplate code.

A ``read_args`` method to handle input to the custom metric.

::

    def read_args():
        """
        Parse command line arguments.
        """
        parser = argparse.ArgumentParser(description='My custom metric')
        parser.add_argument('--test', help='Path to test.')
        parser.add_argument('--result', help='Path to results.')
        parser.add_argument('--output-file', help='The output pickle file.')
    
        # Custom params defined in the config go here
        parser.add_argument('--foo', help='The weight for re-ranking.')
    
        input_args = parser.parse_args()
        return vars(input_args)


You will also need to start the main function with the following lines.
Params specified in the ``config.xml`` are passed as args and are accessible
via the ``args['param-name']`` syntax.

::

    if __name__ == '__main__':
        args = read_args()
    
        params = {'foo': args['foo']}
    
        test_data = ListBasedMetric.read_data_from_file(
            args['test']
        )
        result_data = ListBasedMetric.read_data_from_file(
            args['result'],
            delimiter=','
        )


Adding a row-based metric (i.e., RMSE)
--------------------------------------

For metrics that are based solely upon an item's expected and actual results
(and not the entire lists' results), ``librec-auto`` provides the ``RowBasedMetric``
superclass.

1. Create the new class file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, make a file in your study directory. Name the file something clear.
Let's assume a file named ``custom_rmse_metric.py``

2. Override the ``RowBasedMetric`` methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this ``custom_rmse_metric.py`` file, we'll want to create a subclass of
``RowBasedMetric``, like this:

::
    class CustomRmseMetric(RowBasedMetric):
        ...

We'll also want to override the following methods.

``__init__``
""""""""""""

Override ``__init__`` and set ``self._name`` equal to the name of the metric.
Do not forget to call ``super().__init__``.

::

    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array, output_file) -> None:
        super().__init__(params, test_data, result_data, output_file)
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


Below is a final file for a custom implementation of RMSE

::

    import argparse
    import numpy as np

    from librec_auto.core.eval.metrics.row_based_metric import RowBasedMetric


    def read_args():
        """
        Parse command line arguments.
        """
        parser = argparse.ArgumentParser(description='My custom metric')
        parser.add_argument('--test', help='Path to test.')
        parser.add_argument('--result', help='Path to results.')
        parser.add_argument('--output-file', help='The output pickle file.')

        # Custom params defined in the config go here
        parser.add_argument('--foo', help='The weight for re-ranking.')

        input_args = parser.parse_args()
        return vars(input_args)


    class CustomRmseMetric(RowBasedMetric):
        def __init__(self, params: dict, test_data: np.array,
                    result_data: np.array, output_file) -> None:
            super().__init__(params, test_data, result_data, output_file)
            self._name = 'RMSE'

        def evaluate_row(self, test: np.array, result: np.array):
            test_ranking = test[2]
            result_ranking = result[2]
            return (test_ranking - result_ranking)**2

        def post_row_processing(self, values):
            T = len(values)
            return (sum(values) / T)**0.5


    if __name__ == '__main__':
        args = read_args()

        params = {'foo': args['foo']}

        test_data = CustomRmseMetric.read_data_from_file(args['test'])

        result_data = CustomRmseMetric.read_data_from_file(args['result'],
                                                        delimiter=',')

        custom = CustomRmseMetric(params, test_data, result_data,
                                args['output_file'])

        custom.evaluate()


Adding a list-based metric (i.e., NDCG)
---------------------------------------

For metrics that require the entire result list for computation, ``librec-auto``
provides the ``ListBasedMetric`` superclass, which can be inherited by custom class
metrics.
