.. _SaveCSV:

===============================
Use Fairness Metrics
===============================
:Author:
		Robin Burke
:Version:
		Oct 1st, 2020

1. Introduction
===============

Fairness can be defined in a number of ways for studying the output of recommender systems. We distinguish between *consumer-side* fairness (where consumers are the individuals getting recommendations from the system) and *provider-side* fairness (where providers are the individuals associated with the items being recommended). Consumer-side fairness asks whether the system is fair to different groups of users: for example, job seekers getting recommendations of job listings. Provider-side fairness asks whether the system is fair to different groups of item providers: for example, musical artists whose tracks are being recommended.

2. Feature files
================

All of the fairness metrics in ``librec-auto`` assume a binary-valued feature, which is 1 when the value is protected and 0 when it is unprotected. In order for a metric to work, it will need to get this information from a feature file.

All feature files have the same CSV format. 

::

	id,feature id,value
	
where ``id`` is a user id when user features are being stored and an item feature id when the file has the features of item.

If there are multiple features associated with a given item, there will be multiple lines, one for each feature. If the value for a feature is 0, it can be omitted. 

Feature files are stored in the same directory as the data being used in your study. 


3. Configuration
================

In order to use a fairness metric, you will need to specify the feature file and the protected feature as well as the metric name. 

The feature information is added in the top-level ``features`` section of the configuration file as in this example. 

::

	<features>
		<appender-class>net.librec.data.convertor.appender.ItemFeatureAppender</appender-class>
		<item-feature-file>item-features.csv</item-feature-file>
	</features>

For user features, the ``UserFeatureAppender`` class is used and the ``user-feature-file`` element. 

The information about which feature is considered protected is configured in the ``metric`` section of the configuration with the element  ``protected-feature``. 

4. Available fairness metrics
================

The available metrics for fairness are:

* Statistical parity (``sp``). This metric computes the exposure (% of recommendation list) belonging to the protected and unprotected groups and reports the unprotected value minus the protected value. It ranges from +1 (the recommendation lists consist only of protected items) to -1 (the recommendation lists consist only of unprotected items). 

[Need to fill in additional metrics here.]


