``librec-auto`` is a Python tool for running recommender systems experiments.
It is built on top of the open-source LibRec package, and
can take advantage of the many algorithm and metric implementations there.

The basic element of ``librec-auto`` execution is the "study", which is a series
of experiments carried with a single algorithm, a single data set, and a set
of evaluation metrics. The experiments differ from each other by the hyperparameters
given to the algorithm. ``librec-auto`` allows such studies to be conducted with
minimal experimenter intervention, and supports such capabilities as:

* recommendation result re-ranking
* re-running evaluations without re-computing results
* summarizing results in output graphs
* integration with Slack and Dropbox
