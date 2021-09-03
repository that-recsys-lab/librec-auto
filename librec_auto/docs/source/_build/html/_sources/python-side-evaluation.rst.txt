.. _python-side
======================
Python-side Evaluation
======================


``librec-auto`` supports custom evaluation metrics implemented in python.


Required boilerplate
--------------------

Argument parsing
~~~~~~~~~~~~~~~~

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


Main function
~~~~~~~~~~~~~

You will also need to start the main function with the following lines.
Params specified in the ``config.xml`` are passed to the custom metric files
and are accessible via the ``args['param-name']`` syntax.

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

In this ``custom_rmse_metric.py`` file, we'll want to copy the boilerplate from
above and then create a subclass of ``RowBasedMetric``, like this:

::

    from librec_auto.core.eval.metrics.row_based_metric import RowBasedMetric

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
the test (expected) values for a given ``item,user`` combination. The second
parameter contains the actual values for that ``item,user`` combination. Both are numpy
arrays, and need to be indexed to access the row values. This method should
return the value of the metric for the given ``user,item`` combination.

Every time that ``evaluate_row`` is executed, the results are saved to a ``_scores``
list in the metric class, which we'll access in ``post_row_processing``.

``evaluate_row`` for RMSE follows:

::

	def evaluate_row(self, test: np.array, result: np.array):
	    test_ranking = test[2]
	    result_ranking = result[2]
	    return (test_ranking - result_ranking)**2


``pre_row_processing`` and ``post_row_processing``
""""""""""""""""""""""""""""""""""""""""""""""""""

The ``pre_row_processing`` method allows for setting initial values or for other
processing that should be performed before _any_ of the rows are processed.
Think of this like setting up the metric.

The ``post_row_processing`` method should manipulate ``self._scores`` and return
a single value that represents the final value of the metric.

``post_row_processing`` for RMSE follows:

::

    def post_row_processing(self):
        T = len(self._scores)
        return (sum(self._scores) / T)**0.5


Below is the complete file for an implementation of RMSE.

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

		def post_row_processing(self):
			T = len(self._scores)
			return (sum(self._scores) / T)**0.5


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

Required boilerplate
~~~~~~~~~~~~~~~~~~~~

See above for the argument parsing and main function boilerplate.
These are both required for both row- and list-based metrics, and are
identical for either.

1. Create the new class file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make a file in your study directory. Name is something clear. Let's assume a
file named ``custom_ndcg_metric.py``.

2. Override the ``ListBasedMetric`` methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the ``custom_ndcg_metric.py`` file, we'll want to copy the boilerplate from
above and then then import and instantiate the ``ListBasedMetric`` superclass.

::

    from librec_auto.core.eval.metrics.list_based_metric import ListBasedMetric

    class CustomRmseMetric(ListBasedMetric):
        ...


``__init__``
""""""""""""

Override ``__init__`` and set ``self._name`` equal to the name of the metric.
Do not forget to call ``super().__init__``.

::

    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array, output_file) -> None:
        super().__init__(params, test_data, result_data, output_file)
        self._name = 'RMSE'



``evaluate_user``
"""""""""""""""""

This method produces a metric value for a given user, based on test and result
arrays of user data. These arrays contain values for all rows where this user is
the user.

``evaluate_user`` for NDCG follows:

(Note the ``self._list_size`` is set in ``config.xml``, in ``__init__``, and in
``__main__``.)

::

    def evaluate_user(self, test_user_data: np.array,
                      result_user_data: np.array) -> float:
        rec_num = int(self._list_size)

        idealOrder = test_user_data
        idealDCG = 0.0

        for j in range(min(rec_num, len(idealOrder))):
            idealDCG += ((math.pow(2.0,
                                   len(idealOrder) - j) - 1) /
                         math.log(2.0 + j))

        recDCG = 0.0
        test_user_items = list(test_user_data[:, 1])

        for j in range(rec_num):
            item = int(result_user_data[j][1])
            if item in test_user_items:
                rank = len(test_user_items) - test_user_items.index(
                    item)  # why ground truth?
                recDCG += ((math.pow(2.0, rank) - 1) / math.log(1.0 + j + 1))
        return (recDCG / idealDCG)



``preprocessing`` and ``postprocessing``
""""""""""""""""""""""""""""""""""""""""

``preprocessing`` should be used to set up initial values for the metric that
are not passed from ``config.xml``.

Results from every execution of ``evaluate_user`` are saved to ``self._values``,
which should be accessed in ``postprocessing`` to produce a single final value.

``postprocessing`` for NDCG follows:

::

    def postprocessing(self):
        return np.average(self._values)


``__main__``
""""""""""""

Use the main function to parse any file arguments to class parameters, to
initialize the custom metric class, and to call ``.evaluate()``.


The main function for NDCG follows:

::

	if __name__ == '__main__':
		args = read_args()

		params = {'list_size': args['list_size']}

		test_data = ListBasedMetric.read_data_from_file(
			args['test']
		)
		result_data = ListBasedMetric.read_data_from_file(
			args['result'],
			delimiter=','
		)

		custom = CustomNdcgMetric(params, test_data, result_data,
								args['output_file'])

		custom.evaluate()

Below is the complete file for a custom implementation of NDCG.

::

    import argparse
    import numpy as np
    import math

    from librec_auto.core.eval.metrics.list_based_metric import ListBasedMetric

    def read_args():
        """
        Parse command line arguments.
        """
        parser = argparse.ArgumentParser(description='My custom metric')
        parser.add_argument('--test', help='Path to test.')
        parser.add_argument('--result', help='Path to results.')
        parser.add_argument('--output-file', help='The output pickle file.')

        # Custom params defined in the config go here
        parser.add_argument('--list-size', help='Size of the list for NDCG.')

        input_args = parser.parse_args()
        return vars(input_args)

    class CustomNdcgMetric(ListBasedMetric):
        def __init__(self, params: dict, test_data: np.array,
                    result_data: np.array, output_file: str) -> None:
            super().__init__(params, test_data, result_data, output_file)
            self._name = 'NDCG'
            self._list_size = params['list_size']

        def evaluate_user(self, test_user_data: np.array,
                        result_user_data: np.array) -> float:
            rec_num = int(self._list_size)

            idealOrder = test_user_data
            idealDCG = 0.0

            for j in range(min(rec_num, len(idealOrder))):
                idealDCG += ((math.pow(2.0,
                                    len(idealOrder) - j) - 1) /
                            math.log(2.0 + j))

            recDCG = 0.0
            test_user_items = list(test_user_data[:, 1])

            for j in range(rec_num):
                item = int(result_user_data[j][1])
                if item in test_user_items:
                    rank = len(test_user_items) - test_user_items.index(
                        item)  # why ground truth?
                    recDCG += ((math.pow(2.0, rank) - 1) / math.log(1.0 + j + 1))
            return (recDCG / idealDCG)

        def postprocessing(self):
            return np.average(self._values)


    if __name__ == '__main__':
        args = read_args()


        params = {'list_size': args['list_size']}

        test_data = ListBasedMetric.read_data_from_file(
            args['test']
        )
        result_data = ListBasedMetric.read_data_from_file(
            args['result'],
            delimiter=','
        )

        custom = CustomNdcgMetric(params, test_data, result_data,
                                args['output_file'])

        custom.evaluate()

