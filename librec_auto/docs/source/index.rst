=======================================
librec-auto documentation
=======================================

``librec-auto`` is a Python tool for running recommender systems experiments. It is built on top of the open-source LibRec package, and
can take advantage of the many algorithm and metric implementations there. 

The basic element of ``librec-auto`` execution is the "study", which is a series of experiments carried with a single algorithm, a single data set,
and a set of evaluation metrics. The experiments differ from each other by the hyperparameters given to the algorithm. ``librec-auto`` allows such
studies to be conducted with minimal experimenter intervention, and supports such capabilities as

* recommendation result re-ranking
* re-running evaluations without re-computing results
* summarizing results in output graphs
* integration with Slack and Dropbox

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   
FAQs
======================================


Quickstart guide
================
You can install ''librec-auto'' using pip command as follows:

::

	$ pip install librec-auto

Since ''librec-auto'' uses ''Librec'' library for running the experiments, after installing ''librec-auto'', you will need to also download ''Librec'' library as follows:

::
	
	$ python -m librec_auto install
	
Now, the installation is complete and you can run your experiments using ''librec-auto''.
	

	
The Code
========
	Detailed documentation here
	
HOW-TOs
=======

Using a library
---------------

Sometimes you are running a large number of experiments with many aspects in common, for example, a standard metric configuration or a standard cross-validation methodology. It may be convenient to encode fixed aspects of the work in a library that can be shared across multiple studies implemented in ``librec-auto``.

To create an external library, create an XML file that looks like this:

::

	<librec-auto-library>
		<alg name="itemknn50">
			<class>itemknn</class>
			<similarity type="item">pcc</similarity>
			<neighborhood-size>50</neighborhood-size>
			<shrinkage>50</shrinkage>
		</alg>
	</librec-auto-library>

Note that each internal element (here ``alg``) has an associated ``name`` attribute. This is what is used to look up
elements in the library. You can have any number of elements in a library file.

To use an external library in your ``librec-auto`` configuration file, you first have to import it. Put the following information
at the beginning of your configuration file:

::

	<library>local-library.xml</library>
	
Replacing "local library" with a path to the library file. You can have multiple library files by adding additional ``library`` directives.
They will be consulted in the order that they appear in the file.

To use a predefined element from a library file, you only need to reference it by name. For example, the following element is sufficient to use the item kNN algorithm defined above.

::
	<alg ref="itemknn50"/>
	
You can always override any aspect of the imported element by supplying your own element. For example, to set the shrinkage value to 20, we would
say the following:

::

	<alg ref="itemknn50">
		<shrinkage>20</shrinkage>
	</alg>

All of the other parts of the algorithm specification would be unchanged. 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
