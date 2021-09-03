.. _SaveCSV:

===============================
Rerank
===============================
:Author:
		Ziyue Guo
:Version:
		Feb 09, 2021

1. Introduction
===============

As machine learning systems take over more decision-making, the recommender system may propagate and reinforce human biases. We use the rerank algorithms to maintain the fairness and diversity of the recommender system.

2. Configuration
================

In order to use a rerank algorithm, you will need to specify the rerank method, hyperparameter, maximum length to return, data type (binary or not).

The protected feature is not in configuration but is drawn from the metric section of the configuration file. See discussion under :ref:`

In the ``rerank`` section of the configuration file, for example:

::

    <rerank>  
    <script lang="python3" src="system">
    <script-name>mmr_rerank.py</script-name>
    <param name="max_len">10</param>
    <param name="lambda">
        <value>0.8</value>
        <value>0.5</value>
    </param>
    <param name="binary">True</param>
    </script>
    </rerank>

``mmr_rerank.py`` is the rerank script. 

``max_len`` is the maximum length to return for each user.

``lambda`` is the trade-off hyper-parameter. Higher means better diversity; lower means better accuracy. (for fairstar / FA*IR, this parameter should be “alpha”, which is the error rate of type I error) 

``binary`` shows if the data is binary type.

3. Available rerank algorithms
==============================

The available rerank files are:

FAR rerank, based on W. Liu, R. Burke, Personalizing Fairness-aware Re-ranking

PFAR rerank, based on W. Liu, R. Burke, Personalizing Fairness-aware Re-ranking

MMR rerank, Maximal Marginal Relevance, diversity-based reranking algorithm

FA*IR rerank, based on the paper https://arxiv.org/abs/1706.06368 and the python package fairsearchcore.