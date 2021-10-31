# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import numpy as np
import pytest

try:
    from reco_utils.recommender.rbm.rbm import RBM
except ImportError:
    pass  # skip this import if we are in cpu environment


@pytest.fixture(scope="module")
def init_rbm():
    return {
        "n_hidden": 100,
        "epochs": 10,
        "minibatch": 50,
        "keep_prob": 0.8,
        "learning_rate": 0.002,
        "init_stdv": 0.01,
        "sampling_protocol": [30, 50, 80, 90, 100],
        "display": 20,
    }


@pytest.mark.gpu
def test_class_init(init_rbm):
    model = RBM(
        hidden_units=init_rbm["n_hidden"],
        training_epoch=init_rbm["epochs"],
        minibatch_size=init_rbm["minibatch"],
        keep_prob=init_rbm["keep_prob"],
        learning_rate=init_rbm["learning_rate"],
        init_stdv=init_rbm["init_stdv"],
        sampling_protocol=init_rbm["sampling_protocol"],
        display_epoch=init_rbm["display"],
    )

    # number of hidden units
    assert model.Nhidden == init_rbm["n_hidden"]
    # number of training epochs
    assert model.epochs == init_rbm["epochs"] + 1
    # minibatch size
    assert model.minibatch == init_rbm["minibatch"]
    # keep probability for dropout regulrization
    assert model.keep == init_rbm["keep_prob"]
    # learning rate
    assert model.learning_rate == init_rbm["learning_rate"]
    # standard deviation used to initialize the weight matrix from a normal distribution
    assert model.stdv == init_rbm["init_stdv"]
    # sampling protocol used to increase the number of steps in Gibbs sampling
    assert model.sampling_protocol == init_rbm["sampling_protocol"]
    # number of epochs after which the rmse is displayed
    assert model.display == init_rbm["display"]


@pytest.mark.gpu
def test_train_param_init(init_rbm, affinity_matrix):
    # obtain the train/test set matrices
    Xtr, Xtst = affinity_matrix

    # initialize the model
    model = RBM(
        hidden_units=init_rbm["n_hidden"],
        training_epoch=init_rbm["epochs"],
        minibatch_size=init_rbm["minibatch"],
    )
    # fit the model to the data
    model.fit(Xtr, Xtst)

    # visible units placeholder (tensor)
    model.vu.shape[1] == Xtr.shape[1]
    # weight matrix
    assert model.w.shape == [Xtr.shape[1], init_rbm["n_hidden"]]
    # bias, visible units
    assert model.bv.shape == [1, Xtr.shape[1]]
    # bias, hidden units
    assert model.bh.shape == [1, init_rbm["n_hidden"]]


@pytest.mark.gpu
def test_sampling_funct(init_rbm, affinity_matrix):
    # obtain the train/test set matrices
    Xtr, Xtst = affinity_matrix

    # initialize the model
    model = RBM(
        hidden_units=init_rbm["n_hidden"],
        training_epoch=init_rbm["epochs"],
        minibatch_size=init_rbm["minibatch"],
    )

    def check_sampled_values(sampled, s):
        """
        Check if the elements of the sampled units are in {0,s}
        """
        a = []

        for i in range(0, s + 1):
            l = sampled == i
            a.append(l)

        return sum(a)

    r = Xtr.max()  # obtain the rating scale

    # fit the model to the data
    model.fit(Xtr, Xtst)

    # evaluate the activation probabilities of the hidden units and their sampled values
    phv, h = model.sess.run(model.sample_hidden_units(model.v))

    # check the dimensions of the two matrices
    assert phv.shape == (Xtr.shape[0], 100)
    assert h.shape == (Xtr.shape[0], 100)

    # check that the activation probabilities are in [0,1]
    assert (phv <= 1).all() & (phv >= 0).all()

    # check that the sampled value of the hidden units is either 1 or 0
    assert check_sampled_values(h, 1).all()

    # evaluate the activation probabilities of the visible units and their sampled values
    pvh, v_sampled = model.sess.run(model.sample_visible_units(h))

    assert pvh.shape == (Xtr.shape[0], Xtr.shape[1], r)
    assert v_sampled.shape == Xtr.shape

    # check that the multinomial distribution is normalized over the r classes for all users/items
    assert np.sum(pvh, axis=2) == pytest.approx(np.ones(Xtr.shape))

    # check that the sampled values of the visible units is in [0,r]
    assert check_sampled_values(v_sampled, r).all()
