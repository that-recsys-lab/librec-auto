.. _SaveCSV:

===============================
Use Fairness Metrics
===============================
:Author:
		Robin Burke, Nasim Sonboli
:Version:
		April 30st, 2021

1. Introduction
===============

Fairness can be defined in a number of ways for studying the output of recommender systems. We distinguish between *consumer-side* fairness (where consumers are the individuals getting recommendations from the system) and *provider-side* fairness (where providers are the individuals associated with the items being recommended). Consumer-side fairness asks whether the system is fair to different groups of users: for example, job seekers getting recommendations of job listings. Provider-side fairness asks whether the system is fair to different groups of item providers: for example, musical artists whose tracks are being recommended.

2. Feature files
================

All of the fairness metrics in ``librec-auto`` assume a binary-valued feature, which is 1 when the value is protected and 0 when it is unprotected. In order for a metric to work, it will need to get this information from a feature file.

All feature files have the same CSV format. 

::

	id,feature id,value
	
where ``id`` is a user id when user features are being stored and an item id when the file has the features of items.

If there are multiple features associated with a given id, there will be multiple lines, one for each feature. If the value for a feature is 0, it can be omitted. 

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

For user features, the ``UserFeatureAppender`` class is used and the corresponding ``user-feature-file`` element. 

The information about which feature is considered protected is configured in the ``metric`` section of the configuration with the element  ``protected-feature``. 

4. Available fairness metrics
=============================
The available metrics for fairness are:

Provider-side
~~~~~~~~~~~~~

``* (Provider) Statistical Parity (`psp`).`` This metric computes the exposure (% of recommendation list) belonging to the protected and unprotected groups and reports the unprotected value minus the protected value. It ranges from +1 (the recommendation lists consist only of protected items) to -1 (the recommendation lists consist only of unprotected items).


* Discounted Proportional (Provider) Fairness (`DPPF`)


* P Percent Rule (`PPR`)


* Diversity by feature (`FeatureDiversity`)

D = 1 - \frac{\sum_{i,j \in L}{s(i,j)}}{\frac{k(k-1)}{2}}


* Gini Index (`GiniIndex`)


* Item Coverage (`ICOV`)


Consumer-side
~~~~~~~~~~~~~
* ``Miscalibration (`CalibrationEvaluator` or `miscalib`).`` This method is based on calculating KullbackLeibler Divergence or KL-Divergence. Miscalibration measures the discrepancy between the distribution of the various (past) areas of interest of a user and that of her recommendation list. The higher this divergence is the more unbalanced user's recommendation list is. This method was introduced by Harald Steck in `"Calibrated recommendations." <https://doi.org/10.1145/3240323.3240372>`_ in Proceedings of the 12th ACM conference on recommender systems. ACM, 2018.

.. note::
        - It is zero in case of perfect calibration.
        - It is very sensitive to small discrepancies between the two distributions.
        - It favors more uniform and less extreme distributions.

* `` (Consumer) Statistical Parity (`csp`).`` This metric measures the statistical parity between the total precision of the protected group (p) and that of the unprotected group (u). This metrics measures the difference between the average precision of the protected and unprotected group.

.. math::
    f = (\sum_{n=1}^{|p|} {precision} / |p|) - (\sum_{m=1}^{|u|} {precision} / |u|)

.. note::
    - If the size of both groups is zero, it will return 0.
    - If the size of the unprotected group is zero, the average precision of protected is returned.
    - If the size of the protected group is zero, the average precision of unprotected is returned.
    - otherwise the above formula is computed.

* ``Discounted Proportional (Consumer) Fairness (`DPCF`).`` This metric measures how much utility a group of users gets out of the system compared to everyone else. The below formula computes the sum of the log of this quantity over all groups (discount). Utility is calculated based on Normalized Discounted Cumulative Gain (nDCG) @topN. Larger (less negative) score is better (more fair). This metric is discussed by Kelly, F. P. et al. in `"Rate control for communication networks: shadow prices, proportional fairness and stability." <https://doi.org/10.1057/palgrave.jors.2600523>`_, Journal of the Operational Research society in 1998.

.. math::
    f = \sum_{g \in G}{log(\frac{u_g}{\sum_{g\prime \in G}{u_{g\prime}}})}

* ``Value Unfairness (`VALUNFAIRNESS`).``

.. math::
    U_val = \frac{1}{n} \sum_{j=1}^{n}{\Big|(E_{g}[y]_j - E_{g}[r]_j) - (E_{\neg g}[y]_j - E_{\neg g}[r]_j)\Big|},

    where E_{g}[y]_j is the average predicted score for the jth item from disadvantaged users, E_{\neg g}[y]_j is the average predicted score for advantaged users, E_{g}[r]_j and E_{\neg g}[r]_j are the average ratings for the disadvantaged and advantaged users, respectively.

.. note::
    Absolute Unfairness, Value Unfairness, Over-estimation Unfairness, Under-estimation Unfairness and non-parity Unfairness are proposed by Sirui Yao and Bert Huang in `"Beyond Parity: Fairness Objective for Collaborative Filtering" <https://dl.acm.org/doi/abs/10.5555/3294996.3295052>`_ , NeurIPS 2017.


* ``Absolute Unfairness (`ABSUNFAIRNESS`).`` This metric measures the inconsistency in the absolute estimation error across the user types. Absolute unfairness is unsigned, so it captures a single statistic representing the quality of prediction for each user type. This measure doesn't consider the direction of the error. If one user type has small reconstruction error and the other user type has large reconstruction error, one type of user has the unfair advantage of good recommendation, while the other user type has poor recommendation. One group might always get better recommendations than the other group.

.. math::
    U_abs = \frac{1}{n} \sum_{j=1}^{n}{\Big|\Big|E_{g}[y]_j - E_{g}[r]_j| - |E_{\neg g}[y]_j - E_{\neg g}[r]_j \Big|\Big|}


* ``Under-estimation Unfairness (`UNDERESTIMATE`).`` This metric measures the inconsistency in how much the predictions underestimate the true ratings. Underestimation unfairness is important in settings where missing recommendations are more critical than extra recommendations.

.. math::
    U_{under} = \frac{1}{n} \sum_{j=1}^{n}{\Big|max\left\{0,E_{g}[r]_j - E_{g}[y]_j\right\} - max\left\{0,E_{\neg g}[r]_j - E_{\neg g}[y]_j\right\}\Big|}


* ``Over-estimation Unfairness (`OVERESTIMATE`).``. This metric measures the inconsistency in how much the predictions overestimate the true ratings. Overestimation unfairness may be important in settings where users may be overwhelmed by recommendations, so providing too many recommendations would be especially detrimental. For example, if users must invest llarge amounts of time to evaluate each recommended item, overestimating essentially costs the user time. Thus, uneven amounts of overestimation could cost one type of user more time than the other.

.. math::
    U_{over} = \frac{1}{n} \sum_{j=1}^{n}{\Big|max\left\{0,E_{g}[y]_j - E_{g}[r]_j\right\} - max\left\{0,E_{\neg g}[y]_j - E_{\neg g}[r]_j\right\}\Big|}


* ``Non-parity Unfairness (`NONPAR`).``. This metric is based on the regularization term introduced by Kamishima et al. [17] can be computed as the absolute difference between the overall average ratings of disadvantaged users and those of advantaged users:

.. math::
    U_par =  \left\Big| E_{g}[y] - E_{\neg g}[y] \right\Big|








