from tensorflow.python.keras.layers import Layer
from tensorflow.python.keras import initializers, regularizers, constraints
from tensorflow.python.keras import backend as K
import tensorflow as tf


__all__ = ['LinearKernel', 'L1Kernel', 'L2Kernel', 'PolynomialKernel', 'GaussianKernel','SigmoidKernel']


class LinearKernel(Layer):

    def __init__(self, **kwargs):
        super(LinearKernel, self).__init__(**kwargs)

    def call(self, inputs, **kwargs):
        return K.dot(inputs[0], inputs[1])


class L1Kernel(Layer):

    def __init__(self, **kwargs):
        super(L1Kernel, self).__init__(**kwargs)

    def call(self, inputs, **kwargs):
        x, kernel = K.expand_dims(inputs[0], axis=-1), inputs[1]
        return K.sum(K.abs(x - kernel), axis=-2)


class L2Kernel(Layer):

    def __init__(self, **kwargs):
        super(L2Kernel, self).__init__(**kwargs)

    def call(self, inputs, **kwargs):
        x, kernel = K.expand_dims(inputs[0], axis=-1), inputs[1]
        return K.sqrt(K.sum(K.square(x - kernel), axis=-2) + K.epsilon())


class PolynomialKernel(Layer):

    def __init__(self, p,
                 c=0.0,
                 trainable_c=False,
                 initializer='zeros',
                 regularizer=None,
                 constraint=None,
                 **kwargs):
        super(PolynomialKernel, self).__init__(**kwargs)
        self.p = p
        self.c = c
        self.oc = c
        self.trainable_c = trainable_c
        self.initializer = initializers.get(initializer)
        self.regularizer = regularizers.get(regularizer)
        self.constraint = constraints.get(constraint)

    def build(self, input_shape):
        if self.trainable_c:
            self.c = self.add_weight(
                shape=(),
                initializer=self.initializer,
                regularizer=self.regularizer,
                constraint=self.constraint,
                name='{}_c'.format(self.name),
            )
        super(PolynomialKernel, self).build(input_shape)

    def call(self, inputs, **kwargs):
        return (K.dot(inputs[0], inputs[1]) + self.c) ** self.p

    def get_config(self):
        config = {
            'p': self.p,
            'c': self.oc,
            'trainable_c': self.trainable_c,
            'initializer': initializers.serialize(self.initializer),
            'regularizer': regularizers.serialize(self.regularizer),
            'constraint': initializers.serialize(self.constraint),
        }
        base_config = super(PolynomialKernel, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


class GaussianKernel(Layer):

    def __init__(self, gamma=1.0, trainable_gamma=False, initializer='zeros',
                 regularizer=None,
                 constraint=None, **kwargs):
        super(GaussianKernel, self).__init__(**kwargs)
        self.gamma = gamma
        self.trainable_gamma = trainable_gamma
        self.initializer = initializers.get(initializer)
        self.regularizer = regularizers.get(regularizer)
        self.constraint = constraints.get(constraint)

    def build(self, input_shape):
        if self.trainable_gamma:
            self.gamma = self.add_weight(
                shape=(),
                initializer=self.initializer,
                regularizer=self.regularizer,
                constraint=self.constraint,
                name='{}_gamma'.format(self.name),
            )
        super(GaussianKernel, self).build(input_shape)

    def call(self, inputs, **kwargs):
        x, kernel = K.expand_dims(inputs[0], axis=-1), inputs[1]
        return K.exp(-self.gamma * K.sum(K.square(x - kernel), axis=-2))

    def get_config(self):
        config = {'gamma': self.gamma,
                  'trainable_gamma': self.trainable_gamma,
                  'initializer': initializers.serialize(self.initializer),
                  'regularizer': regularizers.serialize(self.regularizer)
                 }
        base_config = super(GaussianKernel, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

class SigmoidKernel(Layer):

    def __init__(self, **kwargs):
        super(SigmoidKernel, self).__init__(**kwargs)
        self.linear = LinearKernel()

    def call(self, inputs, **kwargs):
        x, w = inputs
        out = self.linear((x,w,None))
        out = tf.math.tanh(out)
        return out