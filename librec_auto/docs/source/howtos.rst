.. _how-to
==========
How-Tos
==========

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


Producing graphical output
--------------------------

There is a post-processing script for producing basic summary plots of your study. This script was primarily designed for studies that make use of cross-validation. Two types of visualization are produced:

* Bar plots with the average metric value for each experiment in the study, for each metric. 
* Box plots that show the distribution of metric values across the different folds of each experiment in a study (if using cross-validation), for each metric.

The script can optionally pop up a browser window that contains the graphics.

In order to use this script, you will need to add it to the post-processing portion of the configuration file. Here is an example:

::

	<script lang="python3" src="system">
		<script-name>result_graphics.py</script-name>
		<param name="browser">true</param>
	</script> 

The plots are stored in the ``post`` directory under the names ``viz-bar-`` *metric*.jpg and ``viz-box-`` *metric*.jpg where *metric*
is the name of the LibRec metric that was calculated.

How to check your configuration files for errors
-------------------------
