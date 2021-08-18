**********************
Algorithm information
**********************
:Author:
		William Kanter
:Version:
		August 18, 2021

,,,,

Similarity
=============

1. PCCSimilarity (pcc)
--------------------------

Pearson Correlation Coefficient (PCC) 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/PCCSimilarity.java>`__

,,,,

2. DiceCoefficientSimilarity (dice)
---------------------------------------

Dice Coefficient Similarity 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/DiceCoefficientSimilarity.java>`__

,,,,

3. MSESimilarity (msesim)
-----------------------------

Mean Square Error Similarity 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/MSESimilarity.java>`__

,,,,

4. BinaryCosineSimilarity (bcos)
------------------------------------

Binary cosine similarity 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/BinaryCosineSimilarity.java>`__

,,,,

5. MSDSimilarity (msd)
--------------------------

Calculate Mean Squared Difference (MSD) similarity proposed by Shardanand and Maes [1995]: Social information filtering: Algorithms for automating "word of mouth"  Mean Squared Difference (MSD) Similarity 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/MSDSimilarity.java>`__

,,,,

6. JaccardSimilarity (jaccard)
----------------------------------

Jaccard Similarity 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/JaccardSimilarity.java>`__

,,,,

7. ExJaccardSimilarity (exjaccard)
--------------------------------------

Extend Jaccard Coefficient 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/ExJaccardSimilarity.java>`__

,,,,

8. CPCSimilarity (cpc)
--------------------------

Constrained Pearson Correlation (CPC) 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/CPCSimilarity.java>`__

,,,,

9. KRCCSimilarity (krcc)
----------------------------

\J. I. Marden, Analyzing and modeling rank data. Boca Raton, Florida: CRC Press, 1996. Mingming Chen etc. A Ranking-oriented Hybrid Approach to QoS-aware Web Service Recommendation. 2015  Kendall Rank Correlation Coefficient 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/KRCCSimilarity.java>`__

,,,,

10. CosineSimilarity (cos)
-----------------------------

Cosine similarity 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/similarity/CosineSimilarity.java>`__

,,,,

Recommender
==============

1. SBPRRecommender (sbpr)
-----------------------------

Social Bayesian Personalized Ranking (SBPR)  Zhao et al., **Leveraging Social Connections to Improve Personalized Ranking for Collaborative Filtering**, CIKM 2014. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/context/ranking/SBPRRecommender.java>`__

,,,,

2. DLambdaFMRecommender (dlambdafm)
---------------------------------------

DLambdaFM Recommender YUAN et al., **LambdaFM: Learning Optimal Ranking with Factorization Machines Using Lambda Surrogates** CIKM 2016. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/context/ranking/DLambdaFMRecommender.java>`__

,,,,

3. TrustSVDRecommender (trustsvd)
-------------------------------------

Guo et al., **TrustSVD: Collaborative Filtering with Both the Explicit and Implicit Influence of User Trust and of Item Ratings**, AAAI 2015. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/context/rating/TrustSVDRecommender.java>`__

,,,,

4. SoRegRecommender (soreg)
-------------------------------

Hao Ma, Dengyong Zhou, Chao Liu, Michael R. Lyu and Irwin King, **Recommender systems with social regularization**, WSDM 2011.  In the original paper, this method is named as "SR2_pcc". For consistency, we rename it as "SoReg" as used by some other papers such as: Tang et al., **Exploiting Local and Global Social Context for Recommendation**, IJCAI 2013. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/context/rating/SoRegRecommender.java>`__

,,,,

5. RSTERecommender (rste)
-----------------------------

Hao Ma, Irwin King and Michael R. Lyu, **Learning to Recommend with Social Trust Ensemble**, SIGIR 2009.  This method is quite time-consuming when dealing with the social influence part. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/context/rating/RSTERecommender.java>`__

,,,,

6. SocialMFRecommender (socialmf)
-------------------------------------

Jamali and Ester, **A matrix factorization technique with trust propagation for recommendation in social networks**, RecSys 2010. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/context/rating/SocialMFRecommender.java>`__

,,,,

7. TrustMFRecommender (trustmf)
-----------------------------------

Yang et al., **Social Collaborative Filtering by Trust**, IJCAI 2013. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/context/rating/TrustMFRecommender.java>`__

,,,,

8. TimeSVDRecommender (timesvd)
-----------------------------------

TimeSVD++ Recommender Koren, **Collaborative Filtering with Temporal Dynamics**, KDD 2009. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/context/rating/TimeSVDRecommender.java>`__

,,,,

9. SoRecRecommender (sorec)
-------------------------------

Hao Ma, Haixuan Yang, Michael R. Lyu and Irwin King, **SoRec: Social recommendation using probabilistic matrix factorization**, ACM CIKM 2008. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/context/rating/SoRecRecommender.java>`__

,,,,

10. CDAERecommender (cdae)
-----------------------------

Yao et al., **Collaborative Denoising Auto-Encoders for Top-N Recommender Systems**, WSDM 2016. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/nn/ranking/CDAERecommender.java>`__

,,,,

11. AutoRecRecommender (autorec)
-----------------------------------

Suvash et al., **AutoRec: Autoencoders Meet Collaborative Filtering**, WWW Companion 2015. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/nn/rating/AutoRecRecommender.java>`__

,,,,

12. ItemKNNRecommender (itemknn)
-----------------------------------

ItemKNNRecommender  optimized by Keqiang Wang 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ItemKNNRecommender.java>`__

,,,,

13. UserKNNRecommender (userknn)
-----------------------------------

UserKNNRecommender  optimized by Keqiang Wang 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/UserKNNRecommender.java>`__

,,,,

14. BHFreeRecommender (bhfree)
---------------------------------

Barbieri et al., **Balancing Prediction and Recommendation Accuracy: Hierarchical Latent Factors for Preference Data**, SDM 2012.   **Remarks:** this class implements the BH-free method. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/BHFreeRecommender.java>`__

,,,,

15. BUCMRecommender (bucm)
-----------------------------

Bayesian UCM: Nicola Barbieri et al., **Modeling Item Selection and Relevance for Accurate Recommendations: a Bayesian Approach**, RecSys 2011.  Thank the paper authors for providing source code and for having valuable discussion. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/BUCMRecommender.java>`__

,,,,

16. NMFItemItemRecommender (nmfitemitem)
-------------------------------------------

Nonnegative Matrix Factorization of the item to item purchase matrix (currently only implicit or binary input supported) NMFItemItem uses as model of the probability distribution P(V) ~ W H V Where V is the observed purchase user item matrix. And W and H are trained matrices. H is the matrix for 'analyzing' the current purchase item history and calculates the assumed latent feature vectors. W is the matrix for 'estimating' the next item purchased from the latent feature vectors. In contrast to this the original Nonnegative Matrix Factorization is a factorization of the item - user matrix.  

#. Lee, Daniel D., and H. Sebastian Seung. "Learning the parts of objects by non-negative matrix factorization." Nature 401.6755 (1999): 788.
 

#. Yuan, Zhijian, and Erkki Oja. "Projective nonnegative matrix factorization for image compression and feature extraction." Image analysis (2005): 333-342.
 

#. Yang, Zhirong, Zhijian Yuan, and Jorma Laaksonen. "Projective non-negative matrix factorizati

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/NMFItemItemRecommender.java>`__

,,,,

17. PLSARecommender (plsa)
-----------------------------

Thomas Hofmann, **Latent semantic models for collaborative filtering**, ACM Transactions on Information Systems. 2004.  

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/PLSARecommender.java>`__

,,,,

18. BLNSLIMFastRecommender (blnslim)
---------------------------------------

This implementation is based on the method proposed by Burke, Robin, Nasim Sonboli, Aldo Ordonez-Gauger, **Balanced neighborhoods for multi-sided fairness in recommendation.** FAT 2018. and Xia Ning and George Karypis, **SLIM: Sparse Linear Methods for Top-N Recommender Systems**, ICDM 2011.  

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/BLNSLIMFastRecommender.java>`__

,,,,

19. AspectModelRecommender (aspectmodelrating)
-------------------------------------------------

Latent class models for collaborative filtering  This implementation refers to the method proposed by Thomas et al. at IJCAI 1999.  **Tempered EM:** Thomas Hofmann, **Latent class models for collaborative filtering**, IJCAI. 1999, 99: 688-693. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/AspectModelRecommender.java>`__

,,,,

20. GBPRRecommender (gbpr)
-----------------------------

Pan and Chen, **GBPR: Group Preference Based Bayesian Personalized Ranking for One-Class Collaborative Filtering**, IJCAI 2013. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/GBPRRecommender.java>`__

,,,,

21. FISMrmseRecommender (fismrmse)
-------------------------------------

Kabbur et al., **FISM: Factored Item Similarity Models for Top-N Recommender Systems**, KDD 2013. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/FISMrmseRecommender.java>`__

,,,,

22. PNMFRecommender (pnmf)
-----------------------------

Projective Nonnegative Matrix Factorization (only implicit or binary feedback supported)  

#. Yuan, Zhijian, and Erkki Oja. "Projective nonnegative matrix factorization for image compression and feature extraction." Image analysis (2005): 333-342.
 

#. Yang, Zhirong, Zhijian Yuan, and Jorma Laaksonen. "Projective non-negative matrix factorization with applications to facial image processing." International Journal of Pattern Recognition and Artificial Intelligence 21.08 (2007): 1353-1362.
 

#. Yang, Zhirong, and Erkki Oja. "Unified development of multiplicative algorithms for linear and quadratic nonnegative matrix factorization." IEEE transactions on neural networks 22.12 (2011): 1878-1891.
 

#. Zhang, He, Zhirong Yang, and Erkki Oja. "Adaptive multiplicative updates for projective nonnegative matrix factorization." International Conference on Neural Information Processing. Springer, Berlin, Heidelberg, 2012.

PNMF tries to model the probability with P(V) ~ W W^T V Where V is the

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/PNMFRecommender.java>`__

,,,,

23. EALSRecommender (eals)
-----------------------------

EALS: efficient Alternating Least Square for Weighted Regularized Matrix Factorization.  This implementation refers to the method proposed by He et al. at SIGIR 2016.  

#. **Real ratings:** Hu et al., Collaborative filtering for implicit feedback datasets, ICDM 2008.
 

#. Fast Matrix Factorization for Online Recommendation With Implicit Feedback, SIGIR 2016
  

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/EALSRecommender.java>`__

,,,,

24. BPRRecommender (bpr)
---------------------------

Rendle et al., **BPR: Bayesian Personalized Ranking from Implicit Feedback**, UAI 2009. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/BPRRecommender.java>`__

,,,,

25. RankALSRecommender (rankals)
-----------------------------------

Takacs and Tikk, **Alternating Least Squares for Personalized Ranking**, RecSys 2012. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/RankALSRecommender.java>`__

,,,,

26. RankSGDRecommender (ranksgd)
-----------------------------------

Jahrer and Toscher, Collaborative Filtering Ensemble for Ranking, JMLR, 2012 (KDD Cup 2011 Track 2). 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/RankSGDRecommender.java>`__

,,,,

27. FISMaucRecommender (fismauc)
-----------------------------------

Kabbur et al., **FISM: Factored Item Similarity Models for Top-N Recommender Systems**, KDD 2013. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/FISMaucRecommender.java>`__

,,,,

28. RankPMFRecommender (rankpmf)
-----------------------------------

The probabilistic matrix factorization (PMF) used in **Collaborative Deep Learning for Recommender Systems**, KDD, 2015. **Collaborative Variational Autoencoder for Recommender Systems**, KDD, 2017. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/RankPMFRecommender.java>`__

,,,,

29. AoBPRRecommender (aobpr)
-------------------------------

AoBPR: BPR with Adaptive Oversampling  Rendle and Freudenthaler, **Improving pairwise learning for item recommendation from implicit feedback**, WSDM 2014. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/AoBPRRecommender.java>`__

,,,,

30. ListRankMFRecommender (listrankmf)
-----------------------------------------

Shi et al., **List-wise learning to rank with matrix factorization for collaborative filtering**, RecSys 2010.  Alpha version 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/ListRankMFRecommender.java>`__

,,,,

31. BPoissMFRecommender (bpoissmf)
-------------------------------------

Prem Gopalan, et al. **Scalable Recommendation with Hierarchical Poisson Factorization**, UAI 2015. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/BPoissMFRecommender.java>`__

,,,,

32. WBPRRecommender (wbpr)
-----------------------------

Gantner et al., **Bayesian Personalized Ranking for Non-Uniformly Sampled Items**, JMLR, 2012. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/WBPRRecommender.java>`__

,,,,

33. LDARecommender (lda)
---------------------------

Latent Dirichlet Allocation for implicit feedback: Tom Griffiths, **Gibbs sampling in the generative model of Latent Dirichlet Allocation**, 2002.   **Remarks:** This implementation of LDA is for implicit feedback, where users are regarded as documents and items as words. To directly apply LDA to explicit ratings, Ian Porteous et al. (AAAI 2008, Section Bi-LDA) mentioned that, one way is to treat items as documents and ratings as words. We did not provide such an LDA implementation for explicit ratings. Instead, we provide recommender {@code URP} as an alternative LDA model for explicit ratings. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/LDARecommender.java>`__

,,,,

34. CoFiSetRecommender (cofiset)
-----------------------------------

Weike Pan, Li Chen, **CoFiSet: Collaborative Filtering via Learning Pairwise Preferences over Item-sets**, SIAM 2013. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/CoFiSetRecommender.java>`__

,,,,

35. CLIMFRecommender (climf)
-------------------------------

Shi et al., **Climf: learning to maximize reciprocal rank with collaborative less-is-more filtering.**, RecSys 2012. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/CLIMFRecommender.java>`__

,,,,

36. BNPPFRecommeder (bnppf)
------------------------------

Gopalan, P., Ruiz, F. J., Ranganath, R., & Blei, D. M. **Bayesian Nonparametric Poisson Factorization for Recommendation Systems**, ICAIS 2014 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/BNPPFRecommeder.java>`__

,,,,

37. ItemBigramRecommender (itembigram)
-----------------------------------------

Hanna M. Wallach, **Topic Modeling: Beyond Bag-of-Words**, ICML 2006. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/ItemBigramRecommender.java>`__

,,,,

38. SLIMRecommender (slim)
-----------------------------

Xia Ning and George Karypis, **SLIM: Sparse Linear Methods for Top-N Recommender Systems**, ICDM 2011.   Related Work:  

#. Levy and Jack, Efficient Top-N Recommendation by Linear Regression, ISRS 2013. This paper reports experimental results on the MovieLens (100K, 10M) and Epinions datasets in terms of precision, MRR and HR@N (i.e., Recall@N).
 

#. Friedman et al., Regularization Paths for Generalized Linear Models via Coordinate Descent, Journal of Statistical Software, 2010.
  

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/SLIMRecommender.java>`__

,,,,

39. WRMFRecommender (wrmf)
-----------------------------

WRMF: Weighted Regularized Matrix Factorization.  This implementation refers to the method proposed by Hu et al. at ICDM 2008.  

#. **Binary ratings:** Pan et al., One-class Collaborative Filtering, ICDM 2008.
 

#. **Real ratings:** Hu et al., Collaborative filtering for implicit feedback datasets, ICDM 2008.
  

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/ranking/WRMFRecommender.java>`__

,,,,

40. LLORMARecommender (llorma)
---------------------------------

Local Low-Rank Matrix Approximation  This implementation refers to the method proposed by Lee et al. at ICML 2013.  **Lcoal Structure:** Joonseok Lee, **Local Low-Rank Matrix Approximation**, ICML. 2013: 82-90. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/LLORMARecommender.java>`__

,,,,

41. AspectModelRecommender (aspectmodelrating)
-------------------------------------------------

Latent class models for collaborative filtering  This implementation refers to the method proposed by Thomas et al. at IJCAI 1999.  **Tempered EM:** Thomas Hofmann, **Latent class models for collaborative filtering**, IJCAI. 1999, 99: 688-693. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/AspectModelRecommender.java>`__

,,,,

42. FMFTRLRecommender (fmftrl)
---------------------------------

Factorization Machine Recommender via Follow The Regularized Leader http://castellanzhang.github.io/2016/10/16/fm_ftrl_softmax 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/FMFTRLRecommender.java>`__

,,,,

43. IRRGRecommender (irrg)
-----------------------------

Zhu Sun, Guibing Guo, and Jie Zhang **Exploiting Implicit Item Relationships for Recommender Systems**, UMAP 2015. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/IRRGRecommender.java>`__

,,,,

44. PMFRecommender (pmf)
---------------------------

#. **PMF:** Ruslan Salakhutdinov and Andriy Mnih, Probabilistic Matrix Factorization, NIPS 2008.
 

#. **RegSVD:** Arkadiusz Paterek, **Improving Regularized Singular Value Decomposition** Collaborative Filtering, Proceedings of KDD Cup and Workshop, 2007.
  

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/PMFRecommender.java>`__

,,,,

45. NMFRecommender (nmf)
---------------------------

Daniel D. Lee and H. Sebastian Seung, **Algorithms for Non-negative Matrix Factorization**, NIPS 2001. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/NMFRecommender.java>`__

,,,,

46. ReMFRecommender (remf)
-----------------------------

Jie Yang, Zhu Sun, Alessandro Bozzon and Jie Zhang **Learning Hierarchical Feature Influence for Recommendation by Recursive Regularization**, RecSys 2016. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/ReMFRecommender.java>`__

,,,,

47. LDCCRecommender (ldcc)
-----------------------------

LDCC: Bayesian Co-clustering (BCC) with Gibbs sampling Wang et al., **Latent Dirichlet Bayesian Co-Clustering**, Machine Learning and Knowledge Discovery in Databases, 2009. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/LDCCRecommender.java>`__

,,,,

48. SVDPlusPlusRecommender (svdpp)
-------------------------------------

SVD++ Recommender Yehuda Koren, **Factorization Meets the Neighborhood: a Multifaceted Collaborative Filtering Model**, KDD 2008. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/SVDPlusPlusRecommender.java>`__

,,,,

49. RFRecRecommender (rfrec)
-------------------------------

Gedikli et al., **RF-Rec: Fast and Accurate Computation of Recommendations based on Rating Frequencies**, IEEE (CEC) 2011, Luxembourg, 2011, pp. 50-57.   **Remark:** This implementation does not support half-star ratings. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/RFRecRecommender.java>`__

,,,,

50. BPMFRecommender (bpmf)
-----------------------------

Salakhutdinov and Mnih, **Bayesian Probabilistic Matrix Factorization using Markov Chain Monte Carlo**, ICML 2008.  Matlab version is provided by the authors via `this link <http://www.utstat.toronto.edu/~rsalakhu/BPMF.html>`__
. This implementation is modified from the BayesianPMF by the PREA package. Bayesian Probabilistic Matrix Factorization

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/BPMFRecommender.java>`__

,,,,

51. FFMRecommender (ffm)
---------------------------

Field-aware Factorization Machines Yuchin Juan, "Field Aware Factorization Machines for CTR Prediction", 10th ACM Conference on Recommender Systems, 2016 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/FFMRecommender.java>`__

,,,,

52. FMSGDRecommender (fmsgd)
-------------------------------

Stochastic Gradient Descent with Square Loss Rendle, Steffen, "Factorization Machines", Proceedings of the 10th IEEE International Conference on Data Mining, 2010 Rendle, Steffen, "Factorization Machines with libFM", ACM Transactions on Intelligent Systems and Technology, 2012 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/FMSGDRecommender.java>`__

,,,,

53. MFALSRecommender (mfals)
-------------------------------

The class implementing the Alternating Least Squares algorithm  The origin paper: Yunhong Zhou, Dennis Wilkinson, Robert Schreiber and Rong Pan. Large-Scale Parallel Collaborative Filtering for the Netflix Prize. Proceedings of the 4th international conference on Algorithmic Aspects in Information and Management. Shanghai, China pp. 337-348, 2008. http://www.hpl.hp.com/personal/Robert_Schreiber/papers/2008%20AAIM%20Netflix/netflix_aaim08(submitted).pdf 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/MFALSRecommender.java>`__

,,,,

54. URPRecommender (urp)
---------------------------

User Rating Profile: a LDA model for rating prediction.   Benjamin Marlin, **Modeling user rating profiles for collaborative filtering**, NIPS 2003.  Nicola Barbieri, **Regularized gibbs sampling for user profiling with soft constraints**, ASONAM 2011. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/URPRecommender.java>`__

,,,,

55. BiasedMFRecommender (biasedmf)
-------------------------------------

Biased Matrix Factorization Recommender 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/BiasedMFRecommender.java>`__

,,,,

56. FMALSRecommender (fmals)
-------------------------------

Factorization Machine Recommender via Alternating Least Square 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/FMALSRecommender.java>`__

,,,,

57. ASVDPlusPlusRecommender (asvdpp)
---------------------------------------

Yehuda Koren, **Factorization Meets the Neighborhood: a Multifaceted Collaborative Filtering Model.**, KDD 2008. Asymmetric SVD++ Recommender 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/ASVDPlusPlusRecommender.java>`__

,,,,

58. GPLSARecommender (gplsa)
-------------------------------

Thomas Hofmann, **Collaborative Filtering via Gaussian Probabilistic Latent Semantic Analysis**, SIGIR 2003.   **Tempered EM:** Thomas Hofmann, **Unsupervised Learning by Probabilistic Latent Semantic Analysis**, Machine Learning, 42, 177�C196, 2001.

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/GPLSARecommender.java>`__

,,,,

59. RBMRecommender (rbm)
---------------------------

This class implementing user-oriented Restricted Boltzmann Machines for Collaborative Filtering  The origin paper:  Salakhutdinov, R., Mnih, A. Hinton, G, Restricted BoltzmanMachines for Collaborative Filtering, To appear inProceedings of the 24thInternational Conference onMachine Learning 2007. http://www.cs.toronto.edu/~rsalakhu/papers/rbmcf.pdf 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/cf/rating/RBMRecommender.java>`__

,,,,

60. SlopeOneRecommender (slopeone)
-------------------------------------

Weighted Slope One: Lemire and Maclachlan, **Slope One Predictors for Online Rating-Based Collaborative Filtering**, SDM 2005. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/ext/SlopeOneRecommender.java>`__

,,,,

61. AssociationRuleRecommender (associationrule)
---------------------------------------------------

Choonho Kim and Juntae Kim, **A Recommendation Algorithm Using Multi-Level Association Rules**, WI 2003.  Simple Association Rule Recommender: we do not consider the item categories (or multi levels) used in the original paper. Besides, we consider all association rules without ruling out weak ones (by setting high support and confidence threshold). 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/ext/AssociationRuleRecommender.java>`__

,,,,

62. PersonalityDiagnosisRecommender (personalitydiagnosis)
-------------------------------------------------------------

Related Work:  

#. `A brief introduction to Personality Diagnosis <http://www.cs.carleton.edu/cs_comps/0607/recommend/recommender/pd.html>`__

  

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/ext/PersonalityDiagnosisRecommender.java>`__

,,,,

63. ExternalRecommender (external)
-------------------------------------

Suppose that you have some predictive ratings (in "pred.txt") generated by an external recommender (e.g., some recommender of MyMediaLite). The predictions are in the format of user-item-prediction. These predictions are corresponding to a test set "test.txt" (user-item-held_out_rating). This class (ExternalRecommender) provides you with the ability to compute predictive performance by setting the training set as "pred.txt" and the test set as "test.txt".    **NOTE:** This approach is not applicable to item recommendation. Thank {@literal Marcel Ackermann} for bringing this demand to my attention. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/ext/ExternalRecommender.java>`__

,,,,

64. BipolarSlopeOneRecommender (bipolarslopeone)
---------------------------------------------------

Biploar Slope One: Lemire and Maclachlan, **Slope One Predictors for Online Rating-Based Collaborative Filtering**, SDM 2005. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/ext/BipolarSlopeOneRecommender.java>`__

,,,,

65. PRankDRecommender (prankd)
---------------------------------

Neil Hurley, **Personalised ranking with diversity**, RecSys 2013.  Related Work:  

#. Jahrer and Toscher, Collaborative Filtering Ensemble for Ranking, JMLR, 2012 (KDD Cup 2011 Track 2).
  

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/ext/PRankDRecommender.java>`__

,,,,

66. UserAverageRecommender (useraverage)
-------------------------------------------

Baseline: predict by the average of target user's ratings

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/baseline/UserAverageRecommender.java>`__

,,,,

67. ItemClusterRecommender (itemcluster)
-------------------------------------------

It is a graphical model that clusters items into K groups for recommendation, as opposite to the {@code UserCluster} recommender. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/baseline/ItemClusterRecommender.java>`__

,,,,

68. MostPopularRecommender (mostpopular)
-------------------------------------------

Baseline: items are weighted by the number of ratings they received.

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/baseline/MostPopularRecommender.java>`__

,,,,

69. UserClusterRecommender (usercluster)
-------------------------------------------

It is a graphical model that clusters users into K groups for recommendation, see reference: Barbieri et al., **Probabilistic Approaches to Recommendations** (Section 2.2), Synthesis Lectures on Data Mining and Knowledge Discovery, 2014. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/baseline/UserClusterRecommender.java>`__

,,,,

70. RandomGuessRecommender (randomguess)
-------------------------------------------

Baseline: predict by a random value in (minRate, maxRate)

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/baseline/RandomGuessRecommender.java>`__

,,,,

71. ItemAverageRecommender (itemaverage)
-------------------------------------------

Baseline: predict by the average of target item's ratings

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/baseline/ItemAverageRecommender.java>`__

,,,,

72. GlobalAverageRecommender (globalaverage)
-----------------------------------------------

Baseline: predict by average rating of all users

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/baseline/GlobalAverageRecommender.java>`__

,,,,

73. ConstantGuessRecommender (constantguess)
-----------------------------------------------

Baseline: predict by a constant rating

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/baseline/ConstantGuessRecommender.java>`__

,,,,

74. EFMRecommender (efm)
---------------------------

EFM Recommender Zhang Y, Lai G, Zhang M, et al. Explicit factor models for explainable recommendation based on phrase-level sentiment analysis[C] {@code Proceedings of the 37th international ACM SIGIR conference on Research & development in information retrieval. ACM, 2014: 83-92}. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/content/EFMRecommender.java>`__

,,,,

75. TopicMFMTRecommender (topicmfmt)
---------------------------------------

TopicMF-MT Recommender Yang Bao, Hui Fang, Jie Zhang. TopicMF: Simultaneously Exploiting Ratings and Reviews for Recommendation[C] {@code 2014, Association for the Advancement of Artificial Intelligence (www.aaai.org)}. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/content/TopicMFMTRecommender.java>`__

,,,,

76. HFTRecommender (hft)
---------------------------

HFT Recommender McAuley J, Leskovec J. Hidden factors and hidden topics: understanding rating dimensions with review text[C] Proceedings of the 7th ACM conference on Recommender systems. ACM, 2013: 165-172. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/content/HFTRecommender.java>`__

,,,,

77. TopicMFATRecommender (topicmfat)
---------------------------------------

TopicMF-AT Recommender Yang Bao, Hui Fang, Jie Zhang. TopicMF: Simultaneously Exploiting Ratings and Reviews for Recommendation[C] {@code 2014, Association for the Advancement of Artificial Intelligence (www.aaai.org)}. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/content/TopicMFATRecommender.java>`__

,,,,

78. TFIDFRecommender (tfidf)
-------------------------------

Created by liuxz on 17-4-29.

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/content/TFIDFRecommender.java>`__

,,,,

79. ConvMFRecommender (convmf)
---------------------------------

ConvMF Recommender Donghyun Kim et al., Convolutional Matrix Factorization for Document Context-aware Recommendation {@code Proceedings of the 10th ACM Conference on Recommender Systems. ACM, 2016.}. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/content/ConvMFRecommender.java>`__

,,,,

80. USGRecommender (usg)
---------------------------

Ye M, Yin P, Lee W C, et al. Exploiting geographical influence for collaborative point-of-interest recommendation[C]// International ACM SIGIR Conference on Research and Development in Information Retrieval. ACM, 2011:325-334. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/poi/USGRecommender.java>`__

,,,,

81. RankGeoFMRecommender (rankgeofm)
---------------------------------------

Li, Xutao,Gao Cong, et al. "Rank-geofm: A ranking based geographical factorization method for point of interest recommendation." SIGIR2015 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/poi/RankGeoFMRecommender.java>`__

,,,,

82. HybridRecommender (hybrid)
---------------------------------

Zhou et al., **Solving the apparent diversity-accuracy dilemma of recommender systems**, Proceedings of the National Academy of Sciences, 2010. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/recommender/hybrid/HybridRecommender.java>`__

,,,,

Eval
=======

1. PrecisionEvaluator (precision)
-------------------------------------

PrecisionEvaluator, calculate precision@n `wikipedia, Precision <https://en.wikipedia.org/wiki/Precision_and_recall>`__
 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/PrecisionEvaluator.java>`__

,,,,

2. AveragePrecisionEvaluator (ap)
-------------------------------------

AveragePrecisionEvaluator, calculate the MAP@n, if you want get MAP, please set top-n = number of items  `wikipedia, MAP <https://en.wikipedia.org/wiki/Information_retrieval>`__ `kaggle, MAP@n <https://www.kaggle.com/wiki/MeanAveragePrecision>`__
 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/AveragePrecisionEvaluator.java>`__

,,,,

1. DiversityByFeaturesEvaluator (featurediversity)
------------------------------------------------------

DiversityEvaluator, average dissimilarity of all pairs of items in the recommended list at a specific cutoff position. This extended version, rebuilds a similarity matrix which uses features instead of ratings. Reference: Avoiding monotony: improving the diversity of recommendation lists, ReSys, 2008 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/DiversityByFeaturesEvaluator.java>`__

,,,,

4. AverageReciprocalHitRankEvaluator (arhr)
-----------------------------------------------

HitRateEvaluator  Xia Ning and George Karypis, **SLIM: Sparse Linear Methods for Top-N Recommender Systems**, ICDM 2011.   They apply a leave-one-out validation method to evaluate the algorithm performance. In each run, each of the datasets is split into a training set and a testing set by randomly selecting one of the non-zero entries of each user and placing it into the testing set. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/AverageReciprocalHitRankEvaluator.java>`__

,,,,

5. EntropyEvaluator (entropy)
---------------------------------

EntropyEvaluator This is a 'Diversity'-Measure, but not necessarily a 'Novelty' or 'Surprisal'-Measure. Look at Section '4.2.3 Item space coverage' of article: Javari, Amin, and Mahdi Jalili. "A probabilistic model to resolve diversity–accuracy challenge of recommendation systems." Knowledge and Information Systems 44.3 (2015): 609-627. Calculates the Entropy within all recommender result list. But please take also attention to the assumed probability space: The probability of an item is assumed to be the probability to be in an recommendation result list. (Estimated by count of this item in all reco list divided by the count of reco lists) This assumption about the probability space is different from the NoveltyEvaluator 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/EntropyEvaluator.java>`__

,,,,

6. ReciprocalRankEvaluator (rr)
-----------------------------------

ReciprocalRankEvaluator, calculate the MRR@n, if you want get MRR, please set top-n = number of items  `wikipedia, MRR <https://en.wikipedia.org/wiki/Mean_reciprocal_rank>`__
 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/ReciprocalRankEvaluator.java>`__

,,,,

7. IdealDCGEvaluator (idcg)
-------------------------------

IdealDCGEvaluator `wikipedia, ideal dcg <https://en.wikipedia.org/wiki/Discounted_cumulative_gain>`__
 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/IdealDCGEvaluator.java>`__

,,,,

8. AUCEvaluator (auc)
-------------------------

AUCEvaluator@n `wikipedia, AUC <https://en.wikipedia.org/wiki/Receiver_operating_characteristic#Area_under_the_curve>`__
 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/AUCEvaluator.java>`__

,,,,

9. GiniIndexEvaluator (giniindex)
-------------------------------------

EntropyEvaluator This is a 'Diversity/Fairness'-Measure, or a horizontal equity measure. Or the degree of inequality in a distribution. Individuals with equal ability/needs should get equal resources. (the need of a special demographic group is not considered.) This is the measure of fair distribution of items in recommendation lists of all the users. The ideal (maximum fairness) case is when this distribution is uniform. The Gini-index of uniform distribution is equal to zero and so smaller values of Gini-index are desired. refer to Fleder, D.M., Hosanagar, K.: Recommender systems and their impact on sales diversity. In: EC ’07: Proceedings of the 8th ACM conference on Electronic commerce, pp. 192–199. ACM, New York, NY, USA (2007). DOI http://doi.acm.org/10.1145/1250910.1250939 The probability of an item is assumed to be the probability to be in a recommendation result list. (Estimated by count of this item in all reco list divided by the count of reco lists) 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/GiniIndexEvaluator.java>`__

,,,,

10. DiversityEvaluator (diversity)
-------------------------------------

DiversityEvaluator, average dissimilarity of all pairs of items in the recommended list at a specific cutoff position. Reference: Avoiding monotony: improving the diversity of recommendation lists, ReSys, 2008 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/DiversityEvaluator.java>`__

,,,,

11. RecallEvaluator (recall)
-------------------------------

RecallEvaluator, calculate recall@n `wikipedia, Recall <https://en.wikipedia.org/wiki/Precision_and_recall>`__
 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/RecallEvaluator.java>`__

,,,,

12. NoveltyEvaluator (novelty)
---------------------------------

NoveltyEvaluator Often also called 'Mean Self-Information' or Surprisal Look at Section '4.2.5 Novelty' of article: Javari, Amin, and Mahdi Jalili. "A probabilistic model to resolve diversity–accuracy challenge of recommendation systems." Knowledge and Information Systems 44.3 (2015): 609-627. Calculates Self-Information of each recommender result list. And then calculates the average of this of all result lists in test set. But please take also attention to the assumed probability space: The probability of an item is assumed to be the purchase probability. (Estimated by items purchased divided by all items purchased.) Surely there is also independence assumed between items. This assumption about the probability space is different from the EntropyEvaluator 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/NoveltyEvaluator.java>`__

,,,,

13. HitRateEvaluator (hitrate)
---------------------------------

HitRateEvaluator  Xia Ning and George Karypis, **SLIM: Sparse Linear Methods for Top-N Recommender Systems**, ICDM 2011.   They apply a leave-one-out validation method to evaluate the algorithm performance. In each run, each of the datasets is split into a training set and a testing set by randomly selecting one of the non-zero entries of each user and placing it into the testing set. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/HitRateEvaluator.java>`__

,,,,

14. NormalizedDCGEvaluator (ndcg)
------------------------------------

NormalizedDCGEvaluator @topN `wikipedia, ideal dcg <https://en.wikipedia.org/wiki/Discounted_cumulative_gain>`__
 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/NormalizedDCGEvaluator.java>`__

,,,,

15. ItemCoverageEvaluator (icov)
-----------------------------------

Finds the ratio of unique items recommended to users to total unique items in dataset(test & train) 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/ranking/ItemCoverageEvaluator.java>`__

,,,,

16. MAEEvaluator (mae)
-------------------------

MAE: mean absolute error 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/rating/MAEEvaluator.java>`__

,,,,

17. RMSEEvaluator (rmse)
---------------------------

RMSE: root mean square error 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/rating/RMSEEvaluator.java>`__

,,,,

18. MPEEvaluator (mpe)
-------------------------

MPE Evaluator 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/rating/MPEEvaluator.java>`__

,,,,

19. MSEEvaluator (mse)
-------------------------

MSE: mean square error 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/rating/MSEEvaluator.java>`__

,,,,

20. MiscalibrationEvaluator (miscalib)
-----------------------------------------

CalibrationEvaluator  Steck, Harald, **"Calibrated recommendations."**, Proceedings of the 12th ACM conference on recommender systems. ACM, 2018.   This method is based on calculating KullbackLeiblerDivergence. Properties (a) it is zero in case of perfect calibration. (b) it is very sensative to small discrepancies between the two distributions. (c) it favors more uniform and less extreme distributions. The overall calibration metric is obtained by averaging over the metric over all users. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/MiscalibrationEvaluator.java>`__

,,,,

21. NonParityUnfairnessEvaluator (nonpar)
--------------------------------------------

Non-parity Unfairness Evaluator is based on the method proposed by T. Kamishima et. al, **Fairness-aware learning through regularization approach**, ICDMW 2011  This metric measures the absolute difference between the overall average ratings of the protected and the unprotected group. consumer-side fairness 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/NonParityUnfairnessEvaluator.java>`__

,,,,

22. DiscountedProportionalPFairnessEvaluator (dppf)
------------------------------------------------------

Discounted Proportional Fairness based on NormalizedDCGEvaluator @topN Kelly, F. P., Maulloo, A. K., & Tan, D. K. (1998). Rate control for communication networks: shadow prices, proportional fairness and stability. Journal of the Operational Research society, 49(3), 237-252. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/DiscountedProportionalPFairnessEvaluator.java>`__

,,,,

23. UnderestimationUnfairnessEvaluator (underestimate)
---------------------------------------------------------

underestiamtion Unfairness Evaluator is based on the method proposed by Sirui Yao and Bert Huang, **Beyond Parity: Fairness Objective for Collaborative Filtering**, NIPS 2017  consumer-side fairness is important where missing recommendations are more critical than extra recommendations. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/UnderestimationUnfairnessEvaluator.java>`__

,,,,

24. DiscountedProportionalCFairnessEvaluator (dpcf)
------------------------------------------------------

Discounted Proportional Fairness based on NormalizedDCGEvaluator @topN Kelly, F. P., Maulloo, A. K., & Tan, D. K. (1998). Rate control for communication networks: shadow prices, proportional fairness and stability. Journal of the Operational Research society, 49(3), 237-252. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/DiscountedProportionalCFairnessEvaluator.java>`__

,,,,

25. AbsoluteUnfairnessEvaluator (absunfairness)
--------------------------------------------------

Absolute Unfairness Evaluator is based on the method proposed by Sirui Yao and Bert Huang, **Beyond Parity: Fairness Objective for Collaborative Filtering**, NIPS 2017  This metric measures the inconsistency in absolute estimation error across the user types consumer-side fairness it captures a single statistic representing the quality of prediction for each user type. One group might always get better recommendations than the other group. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/AbsoluteUnfairnessEvaluator.java>`__

,,,,

26. PStatisticalParityEvaluator (psp)
----------------------------------------



`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/PStatisticalParityEvaluator.java>`__

,,,,

27. ValueUnfairnessEvaluator (valunfairness)
-----------------------------------------------

Value Unfairness Evaluator is based on the method proposed by Sirui Yao and Bert Huang, **Beyond Parity: Fairness Objective for Collaborative Filtering**, NIPS 2017  This metric measures the signed estimation error across the user types consumer-side fairness Value unfairness occurs when one class of users is consistently given higher or lower predictions than their true preferences. larger values shows that estimations for one class is consistently over-estimated and the estimations for the other class is consistently under-estimated. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/ValueUnfairnessEvaluator.java>`__

,,,,

28. CStatisticalParityEvaluator (csp)
----------------------------------------



`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/CStatisticalParityEvaluator.java>`__

,,,,

29. PPercentRuleEvaluator (ppr)
----------------------------------

p% rule states that the ratio between the percentage of subjects having a certain sensitive attribute value assigned the postive decision outcome and the percentage of subjects not having that value also assigned the positive outcome should be no less than p%. The rule implies that each group has a positive probability of **at least p%** of the other group. the 100%-rule implies perfect removal of disparate impact on group=level fairness and a large value of p is preferred. The final result should be greater than or equal to "p%" to be considered fair. min(a/b, b/a) >= p/100 a = P[Y=1|s=1] & b = P[Y=1|s=0] This is derived from the "80%-rule" supported by the U.S. Equal Employment Opportunity Commission. PPercentRuleEvaluator is based on the 80%-rule discussed by Dan Biddle, **Adverse Impact and Test Validation: A Practitioner's Guide to Valid amd Defensible Employment Testing** 2006  p% rule is discussed in Zafar, Muhammad Bilal and Valera, Isabel and Rogrigez, Manuel Gomes and Gummadi

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/PPercentRuleEvaluator.java>`__

,,,,

30. OverestimationUnfairnessEvaluator (overestimate)
-------------------------------------------------------

Overestimation Unfairness Evaluator is based on the method proposed by Sirui Yao and Bert Huang, **Beyond Parity: Fairness Objective for Collaborative Filtering**, NIPS 2017  consumer-side fairness It is important in settings where users may be overwhelmed by recommendations, so too many recoms becomes detrimental. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/eval/fairness/OverestimationUnfairnessEvaluator.java>`__

,,,,

Filter
=========

1. GenericRecommendedFilter (generic)
-----------------------------------------

Recommended Filter 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/filter/GenericRecommendedFilter.java>`__

,,,,

Data
=======

1. DocumentDataAppender (document)
--------------------------------------

A DocumentDataAppender is a class to process and store document appender data. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/data/convertor/appender/DocumentDataAppender.java>`__

,,,,

2. LOOCVDataSplitter (loocv)
--------------------------------

Leave one out Splitter Leave random or the last one user/item out as test set and the rest treated as the train set. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/data/splitter/LOOCVDataSplitter.java>`__

,,,,

3. GivenTestSetDataSplitter (testset)
-----------------------------------------

Given Test Set Data Splitter Get test set from specified path Test set and train set should be in the same directory. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/data/splitter/GivenTestSetDataSplitter.java>`__

,,,,

4. GivenNDataSplitter (givenn)
----------------------------------

GivenN Data Splitter Split dataset into train set and test set by given number. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/data/splitter/GivenNDataSplitter.java>`__

,,,,

5. KCVDataSplitter (kcv)
----------------------------

K-fold Cross Validation Data Splitter 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/data/splitter/KCVDataSplitter.java>`__

,,,,

6. RatioDataSplitter (ratio)
--------------------------------

Ratio Data Splitter. Split dataset into train set, test set, valid set by ratio. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/data/splitter/RatioDataSplitter.java>`__

,,,,

7. TextDataModel (text)
---------------------------

A TextDataModel represents a data access class to the CSV format input. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/data/model/TextDataModel.java>`__

,,,,

8. JDBCDataModel (jdbc)
---------------------------

A JDBCDataModel represents a data access class to the database format input. 

`Github source <https://github.com/that-recsys-lab/librec/tree/3.0.0/core/src/main/java/net/librec/data/model/JDBCDataModel.java>`__


