.. _usefairnessmetrics:

===============================
Use Fairness Metrics
===============================
:Author:
		Nasim Sonboli, Robin Burke
:Version:
		April 2nd, 2021

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

Note that only a single (binary) protected feature across algorithm, metric, and re-ranking is currently supported. We expect to generalize this capability in future releases.

4. Available fairness metrics
=============================
The available metrics for fairness are:

Provider-side
~~~~~~~~~~~~~

* ``(Provider) Statistical Parity (`psp`).`` This metric computes the exposure (% of recommendation list) belonging to the protected and unprotected groups and reports the unprotected value minus the protected value. It ranges from +1 (the recommendation lists consist only of protected items) to -1 (the recommendation lists consist only of unprotected items).


* ``Discounted Proportional (Provider) Fairness (`DPPF`).`` This metric measures how much utility a group of (item) provider gets out of the system compared to everyone else. The utility of a provider group is calcualted by summation of DCGs of all the items belonging to the provider group. Utility is calculated based on Normalized Discounted Cumulative Gain (nDCG) @topN. Larger (less negative) score is better (more fair). This metric is discussed by Kelly, F. P. et al. in `"Rate control for communication networks: shadow prices, proportional fairness and stability." <https://doi.org/10.1057/palgrave.jors.2600523>`_, Journal of the Operational Research society in 1998.


* ``P Percent Rule (`PPR`).`` This metric states that the ratio between the percentage of subjects having a certain sensitive attribute value assigned the positive decision outcome and the percentage of subjects not having that value also assigned the positive outcome should be no less than p%. The rule implies that each group has a positive probability of at least p% of the other group. The 100%-rule implies perfect removal of disparate impact on group-level fairness and a large value of p is preferred. The final result should be greater than or equal to "p%" to be considered fair. This is derived from the "80%-rule" supported by the U.S. Equal Employment Opportunity Commission. PPercentRuleEvaluator is based on the 80%-rule discussed by Dan Biddle in "Adverse Impact and Test Validation: A Practitioner's Guide to Valid and Defensible Employment Testing" book, 2006. It is also based on the p% rule discussed by Zafar et al. in `"Fairness Constraints: Mechanisms for Fair Classification" <http://proceedings.mlr.press/v54/zafar17a.html>`_, AISTATS 2017.

.. math::
    \\ min(\frac{a}{b}, \frac{b}{a}) >= p/100 \\
    where \ a = P[Y=1|s=1], \\ and \ b = P[Y=1|s=0]


* ``Diversity by feature (`FeatureDiversity`).`` This metric is calculated as the average dissimilarity of all pairs of items in the recommended list at a specific cutoff position. Although, in this extended version, the similarity matrix is computed based on the similarities in item features instead of ratings over an item. For more details please refer to `"Avoiding monotony: improving the diversity of recommendation lists" <https://doi.org/10.1145/1454008.1454030>`_

.. math::
    D = 1 - \frac{\sum_{i,j \in L}{s(i,j)}}{\frac{k(k-1)}{2}}


* ``Gini Index (`GiniIndex`).`` This metric is a horizontal equity measure and it calculates the degree of inequality in a distribution. Fairness in this context means individuals with equal ability/needs should get equal resources. This is the measure of fair distribution of items in recommendation lists of all the users. The probability of an item is assumed to be the probability to be in a recommendation result list (Estimated by count of this item in all recommendation list divided by the count of recommendation lists). The ideal (maximum fairness) case is when this distribution is uniform. The Gini-index of uniform distribution is equal to zero and so smaller values of Gini-index are desired. For more details refer to `"Recommender systems and their impact on sales diversity" <http://doi.acm.org/10.1145/1250910.1250939>`_ by Fleder, D.M., Hosanagar, K in the Proceedings of the 8th ACM conference on Electronic commerce 2007.


* ``Item Coverage (`ICOV`).`` This metric calculates the ratio of the unique items recommended to users to the total unique items in dataset (test & train).



Consumer-side
~~~~~~~~~~~~~
* `` (Consumer) Statistical Parity (`csp`).`` This metric measures the statistical parity between the total precision of the protected group (p) and that of the unprotected group (u). This metrics measures the difference between the average precision of the protected and unprotected group.

.. math::
    f = (\sum_{n=1}^{|p|} {precision} / |p|) - (\sum_{m=1}^{|u|} {precision} / |u|)

.. note::
    - If the size of both groups is zero, it will return 0.
    - If the size of the unprotected group is zero, the average precision of protected is returned.
    - If the size of the protected group is zero, the average precision of unprotected is returned.
    - otherwise the above formula is computed.


* ``Miscalibration (`CalibrationEvaluator` or `miscalib`).`` This method is based on calculating KullbackLeibler Divergence or KL-Divergence. Miscalibration measures the discrepancy between the distribution of the various (past) areas of interest of a user and that of her recommendation list. The higher this divergence is the more unbalanced user's recommendation list is. This method was introduced by Harald Steck in `"Calibrated recommendations." <https://doi.org/10.1145/3240323.3240372>`_ in Proceedings of the 12th ACM conference on recommender systems. ACM, 2018.

.. note::
        - It is zero in case of perfect calibration.
        - It is very sensitive to small discrepancies between the two distributions.
        - It favors more uniform and less extreme distributions.


* ``Discounted Proportional (Consumer) Fairness (`DPCF`).`` This metric measures how much utility a group of users gets out of the system compared to everyone else. The below formula computes the sum of the log of this quantity over all groups (discount). Utility is calculated based on Normalized Discounted Cumulative Gain (nDCG) @topN. Larger (less negative) score is better (more fair). This metric is discussed by Kelly, F. P. et al. in `"Rate control for communication networks: shadow prices, proportional fairness and stability." <https://doi.org/10.1057/palgrave.jors.2600523>`_, Journal of the Operational Research society in 1998.

.. math::
    f = \sum_{g \in G}{log(\frac{u_g}{\sum_{g\prime \in G}{u_{g\prime}}})}

* ``Value Unfairness (`VALUNFAIRNESS`).`` This unfairness occurs when one class of users is consistently given higher or lower predictions than their true preferences. Larger values shows that estimations for one class is consistently over-estimated and the estimations for the other class is consistently under-estimated.

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








