==================
Configuration File
==================

librec-auto uses an XML configuration file to specify all aspects of the experimental pipeline. A configuration file defines a *study*, which computes evaluation results for a single algorithm and a single data set, possibly over multiple choices of hyperparameters, each of which constitutes an *experiment*. The configuration file is divided into sections, some of which are optional.

Global elements (all optional)
============

Example
::
	<random-seed>202001</random-seed>
	<thread-count>1</thread-count>
	<library src="system">default-algorithms.xml</library>


``random-seed``: An integer that will be used as the seed for any randomized actions that the platform takes. This ensures repeatability for experiments.

``thread-count``: If this is greater than zero, librec-auto will spawn multiple threads for various tasks, including parallel execution of  experiments.

``library``: There can be multiple ``library`` elements, from which algorithms, metrics and other elements can be imported. There is a default system library for algorithms (referenced in the example). An element from the library can be imported using the ``ref`` attribute.

    Example: ``<alg ref="alg:biasedmf"/>`` refers to the ``biasedmf`` (Biased Matrix Factorization) algorithm as implemented in LibRec with the default hyperparameters given the library. The library file can be consulted to see what hyperparameters the algorithm accepts. These can be overridden by local declarations in the configuration file.

Additional information about libraries is available in :ref:`Using a library`

Data Section
============

Example
::
	<data>
		<data-dir>../data</data-dir>
		<format>UIR</format>
		<data-file format="text">ratings.csv</data-file>
	</data>


The data section indicates where the data for the study can be found. The data can be in any convenient place. However, ``librec-auto`` will need to be able to write to this directory since it will by default add new data split directories here. The ``data-file`` file name is considered to be relative to the data directory.

Note that there are two different places where the format is specified. The ``format`` element indicates the columns in the ratings file. The options are ``UIR`` (user id, item id, rating) and `UIRT` (adding time), The ``format`` attribute is the file format of the ratings file: LibRec supports text and AIFF file formats.

If you are using fixed training and test files, you do not use the ``data-file`` element, but instead use the ``train-file`` element and the ``test-file`` element.

Feature Section (optional)
===============

For algorithms and / or metrics that make use of features associated with items and users, the ``feature`` element can be included.

Example:
::
    <features>
		<appender-class>net.librec.data.convertor.appender.ItemFeatureAppender</appender-class>
		<item-feature-file>item-features.csv</item-feature-file>
	</features>


There are two feature appender classes ``net.librec.data.convertor.appender.ItemFeatureAppender`` and ``net.librec.data.convertor.appender.UserFeatureAppender``. The associated feature file is expected to be located in the data directory and has the following format: item id (or user id), feature name, feature value. This is a sparse format, so rows with zero values can be omitted. If the value is binary, the feature value can also be omitted and all included rows will have a feature value of 1.

Splitter Section
================
Example:
::
	<splitter>
		<model count="5">kcv</model>
		<dim>userfixed</dim>
		<ratio>0.8</ratio>
		<save>true</save>
	</splitter>

The above example will perform five-fold cross-validation using the ``userfixed`` strategy, using 80% of the data for training and 20% for testing in each fold. The splits will be saved to the data directory, and can be re-used in subsequent experimentation.

LibRec supports multiple types of data splitting: given n, given test set, leave one out, ratio, and k-fold cross validation. Ratio and kcv have a number of selection strategies (picked using the ``dim`` element): rating (random selection across all ratings), user (random selection by user), item (random selection by item), userfixed (fixed number of items chosen randomly for the user), ratingdate, userdate, itemdate (for the ``ratio`` option, choose the oldest items for training).

Algorithm Section
=================
Example:
::
	<alg>
		<class>biasedmf</class>
		<similarity type="item">pcc</similarity>
		<iterator-max>25</iterator-max>
		<item-reg>0.05</item-reg>
		<num-factors>20</num-factors>
	</alg>

LibRec supports more than 70 recommendation algorithms. See :ref:`Supported Algorithms` for a list. Each has its own hyperparameters. Users are encouraged to consult the LibRec documentation and (more helpfully) source code for specific references to the algorithm details and links to original research. The ``class`` element refers to the algorithm name or (rarely necessary) the specific Java class name of the algorithm to be invoked. Algorithm names are defined in the LibRec source code in the file ``librec/core/src/main/resources/driver.classes.props``.


The default algorithms library (described in :ref:`Using a library`) contains a number of the most common algorithms and complete lists of their hyperparameters with default values.

Typically, a study will consist of multiple experiments over different algorithm hyperparameters. ``librec-auto`` supports both grid search and Bayesian black-box optimization (using ``scikit-optimize``). To use the grid search function, replace a given hyperparameter value with a list of values, delimited with the ``value`` element. For example:

::
		<item-reg><value>0.001</value><value>0.01</value><value>0.05</value></item-reg>

This element would substitute for the ``item-reg`` element in the algorithm specification above and tell the system to conduct experiments using the three given item regularization weights.

Any number of hyperparameters can be searched over. ``libec-auto`` will conduct an experiment for every combination of values (Cartesian product), so the number of experiments can be quite large.

For information on black-box optimization, see :ref:`black-box`. (TODO: Write this)

Optimize Section (optional)
==============
The black-box optimization capability requires the use of a separate *optimize* element to specify what metric is used for optimization and how many iterations are to be performed. For example,

::

    <optimize><metric>precision</metric>
        <iterations>25</iterations></optimize>

By default, the first 20 iterations are random samples from the parameter space, so the optimization procedure does not kick in until after this point.

This option cannot be combined with grid search. If it is used, instead of providing a list of values associated with a parameter (the ``value`` element), we provide an upper and lower bound to the search range.

::

    <item-reg><lower>0.01</lower>
          <upper>0.05</upper></item-reg>

Note that black-box optimization can only be used for numeric parameters. Options that are configured as discrete choices (similarity metrics, for example) are not currently supported.

Metrics Section
===============
Example:
::
	<metric>
		<ranking>true</ranking>
		<list-size>10</list-size>
		<class>ndcg,precision,psp</class>
		<protected-feature>new</protected-feature>
	</metric>

A study can employ multiple metrics. See :ref:`Supported Algorithms` for information about the wide variety of metrics implemented in LibRec. Error-based metrics (like RMSE) require the ``ranking`` element to be set to false. Ranking metrics (like nDCG) require ``ranking`` to be true and a list-size to be specified. a

Note: Despite the fact that this is the section for metrics, the ``list-size`` element here controls the lists that the algorithm computes. (We expect this behavior to change in future releases.) This means that if you are using a re-ranking design, the list size given here should be the larger pre-re-ranking value. Your re-ranking script should take a different parameter that controls the length of the output list. Therefore, it is possible that the ``list-size`` element says 100, but the value computed might actually be nDCG@10 because the re-ranker has truncated lists to length 10.

Fairness-aware metrics (like ``psp`` (Provider-side Statistical Parity) seen here) will require a ``protected-feature`` element. In the current release, this must be a binary feature. Items (or users) will associated feature value of 1 will be considered "protected" for the purposes of a fairness metric. This value is also used by fairness-aware algorithms in LibRec (currently only Balanced Neighborhood SLIM).

Additional information on using fairness metrics can be found at :ref:`Use Fairness Metrics`.

Rerank Section (optional)
==============
For a study that includes re-ranking, the re-ranking script is specified here. Note that all re-ranking is done by external script resources and these can be easily crafted or adapted by experimenters. Currently, only Python scripts are supported.

Example:
::
	<rerank>
		<script lang="python3" src="system">
			<script-name>far-rerank.py</script-name>
			<param name="max_len">10</param>
			<param name="lambda">
				<value>0.3</value>
				<value>0.0</value>
			</param>
			<param name="binary">False</param>
		</script>
	</rerank>

By default, a re-ranker is passed the following information:

- The path to the configuration file. Loading this file will enable the re-ranker to access information about all aspects of the experiment being run.
- The path to the original algorithm results. The script will read from these results.
- The path to the results directory where output should be stored.
- Any other parameters specified with ``param`` elements.

Note that ``param`` elements can have multiple values and therefore can be part of algorithm optimization.

Additional information is available at :ref:`Rerank`.

Post-Processing Section
=======================
``librec-auto`` supports the post-processing of study results. There are existing scripts for producing simple visualizations (:ref:`Producing graphical output`), for producing CSV files for further analysis (:ref:`Produce CSV Output`), and for posting experimental results to Slack and Dropbox (:ref:`Integrations`).
