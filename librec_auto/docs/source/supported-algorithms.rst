Supported Algorithms
====================

.. This content is currently included in the run-a-study page

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
	log4j
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
	userknn
	usg-test
	wbpr
	wrmf


Custom algorithms
-----------------

You can also add your own algorithms to ``librec-auto``.


To add a new metric, first create a new file in the ``core/eval/metrics`` directory. Add a class in that directory that is either a subclass of ``ListBasedMetric`` or ``RowBasedMetric``.

If you are using ``ListBasedMetric``, implement the ``evaluate`` method. If you are using an instance of ``RowBasedMetric``, implement the ``evaluate_row`` and ``post_row_processing`` methods at minimum.

Then, add a key/value pair to the ``metric_name_to_class`` dictionary at the top of the ``core/cmd/eval_cmd.py`` file.

Now you're ready to add this new class to your configuration file. Add a metric element with the python attribute set to true and the name value set to the name that you chose in the ``metric_name_to_class`` dictionary. Pass any parameters as necessary.

You can access these parameters as key/value dictionary pairs inside your Metric class instance with ``self._params``.

::

	<metric python="true">
		<!-- name is the class name for the metric -->
		<name>ndcg</name>
		<params>
			<foo>bar</foo>
		</params>
	</metric>