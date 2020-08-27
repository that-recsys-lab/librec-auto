# Librec-auto

## Purpose

The librec-auto project aims to automate recommender system studies using Librec. 

## Workflow

The workflow of an study involves identifying appropriate data, creating 
training / test splits, implementing or choosing algorithms, running experiments
(possibly with a range of different parameters), and reporting on the results.

## Configuration

Librec-auto uses an XML-based configuration system similar to Maven or Ant. 

## Project structure

This directory contains the Python libraries for the librec_auto module. There are two other affiliated
respositories:

- librec-auto-java: Contains the java source for the wrapper between LibRec () and librec-auto, which is implemented
in the jar file: auto.jar.
- librec-auto-sample: Contains sample data and configuration files that can be used to explore the functionality
of librec-auto

top-level
* /jar
    * Contains the jar files for LibRec and the wrapper. 
* /rules
    * Contains the rules for translating configuration data to LibRec properties format.
* /librec_auto
	* Contains the Python code for the project.
* /doc
	* Contains documentation for the project
* /test
	* Contains the unit tests (not many right now)

## Code Formatting

We use [yapf](https://github.com/google/yapf) for python code formatting.
To format the whole codebase, run:

```
yapf . -i --recursive
```
