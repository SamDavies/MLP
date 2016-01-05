from unittest import TestCase

import numpy
from numpy.testing import assert_array_equal, assert_array_almost_equal

from mlp.costs import CECost
from mlp.dataset import MNISTDataProvider, add_batches
from mlp.layers import Sigmoid, Softmax, Linear, MLP
from mlp.noise import DropoutNoise, NoiseMaker
from mlp.optimisers import AutoEncoder

__author__ = 'Sam Davies'


class AutoEncoderTestCase(TestCase):
    def test_pretrain(self):
        """ Ensure that a single layer can be trained """
        # Given
        train_dp = MNISTDataProvider(dset='train', batch_size=100, max_num_batches=1, randomize=True)
        valid_dp = MNISTDataProvider(dset='valid', batch_size=100, max_num_batches=1, randomize=False)

        train_dp.reset()
        valid_dp.reset()

        rng = numpy.random.RandomState([2015, 10, 10])
        rng_state = rng.get_state()

        cost = CECost()
        model = MLP(cost=cost)
        model.add_layer(Sigmoid(idim=784, odim=100, rng=rng))
        model.add_layer(Sigmoid(idim=100, odim=100, rng=rng))
        model.add_layer(Softmax(idim=100, odim=10, rng=rng))
        auto_encoder = AutoEncoder(learning_rate=0.5, max_epochs=5)
        auto_encoder.pretrain(model, train_iter=train_dp, valid_iter=valid_dp)
        self.assertAlmostEqual(model.layers[0].W[0][0], 0.03, delta=0.005)
        self.assertAlmostEqual(model.layers[1].W[0][0], -0.03, delta=0.005)
        self.assertAlmostEqual(model.layers[2].W[0][0], 0.097, delta=0.005)


class NoiseTestCase(TestCase):
    def setUp(self):
        self.rng = numpy.random.RandomState([2015, 10, 10])
        self.rng_state = self.rng.get_state()

    def test_add_noise(self):
        train_dp = MNISTDataProvider(dset='train', batch_size=100, max_num_batches=1, randomize=True)
        train_dp.reset()

        noise_type = DropoutNoise(dropout_prob=0.5)
        noise_maker = NoiseMaker(data_set=train_dp, num_batches=1, noise=noise_type)
        new_batches = noise_maker.make_examples(rng=self.rng)
        add_batches(train_dp, new_batches)

        self.assertEqual(len(train_dp.x), 50100)
        self.assertEqual(train_dp.t[99], train_dp.t[50099])
