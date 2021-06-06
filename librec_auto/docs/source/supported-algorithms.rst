.. _supported
====================
Supported Algorithms
====================


``librec-auto`` supports all of the algorithms in ``Librec``.
As of September 15, 2020, the following algorithms are supported:

::

	aobpr
	aspectmodelranking
	aspectmodelrating
	associationrule
	asvdpp
	autorec
	bhfree
	biasedmf
	biasedmf
	bipolarslopeone
	bnppf
	bpmf
	bpoissmf
	bpr
	bucm
	cdae
	climf
	cofiset
	constantguess
	convmf
	cptf
	dlambdafm
	eals
	efm
	ensemble-linear
	ensemble-stacking
	external
	ffm
	fismauc
	fismrmse
	fmals
	fmftrl
	fmsgd
	gbpr
	globalaverage
	gplsa
	hft
	hybrid
	irrg
	itemaverage
	itembigram
	itemcluster
	itemknn
	itemknn
	lda
	ldcc
	librec-default
	librec
	listrankmf
	llorma
	mfals
	mostpopular
	nmf
	nmfitemitem
	personalitydiagnosis
	pitf
	plsa
	pmf
	pnmf
	prankd
	randomguess
	rankals
	rankgeofm
	rankpmf
	ranksgd
	rbm
	remf
	rfrec
	rste
	sbpr
	slim
	slopeone
	socialmf
	sorec
	soreg
	svdpp
	tfidf
	timesvd
	topicmfat
	topicmfmt
	trustmf
	trustsvd
	urp
	useraverage
	usercluster
	userknn
	usg-test
	wbpr
	wrmf


Custom algorithms
-----------------

In future releases, you will be able to add your own algorithms to ``librec-auto``.

Supported metrics
=============

``librec-auto`` supports all of the metrics in ``Librec``.
As of September 15, 2020, the following metrics are supported:

::

    auc
    ap (Average Precision)
    arhr (Average Reciprocal Hit Rate)
    diversity
    hitrate
    ndcg
    precision
    recall
    rr (Reciprocal Rank)
    featurediversity
    novelty
    entropy
    giniindex
    icov (Item Coverage)
    mae
    mpe
    mse
    rmse
    csp (Consumer-side Statistical Parity of nDCG)
    psp (Provider-side Statistical Parity of exposure)
    miscalib (Miscalibration)
    dppf (Discounted Proportional Provider-side Fairness)
    dpcf (Discounted Proportional Consumer-side Fairness)
    nonpar (NonParityUnfairness)
    valunfairness (Value Unfairness)
    absunfairness (Absolute Unfairness)
    overestimate (Overestimation Unfairness)
    underestimate (Underestimation Unfairness)
    ppr (PPercent Rule as applied to provider exposure)

Custom metrics
-------------

To add a new metric, see discussion in :ref:`python-side`