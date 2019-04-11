# Librec-auto

## Purpose

The librec-auto project aims to automate recommender system experimens using Librec. 

## Workflow

The workflow of an experiment involves identifying appropriate data, creating 
training / test splits, implementing or choosing algorithms, running experiments
(possibly with a range of different parameters), and reporting on the results.

## Configuration

Librec-auto uses an XML-based configuration system similar to Maven or Ant. 

## Project structure

top-level
* /lib
	* /librec
		* Maven project contains the librec 2.0 project submodule to the rburke fork of librec
	* /auto
		* Maven project contains the Java component of librec-auto, depends on librec
* /librec-auto
	* contains the Python code for the project, depends on librec and auto
* /doc
	* contains documentation for the project
* /test
	* contains the tests

	

