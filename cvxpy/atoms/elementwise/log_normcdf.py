"""
Copyright 2021 the CVXPY developers
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import functools

import scipy.sparse
import numpy as np

from cvxpy.atoms.affine.reshape import reshape
from cvxpy.atoms.affine.sum import sum as sum_
from cvxpy.atoms.elementwise.maximum import maximum


def log_normcdf(x):
    """Elementwise log of the cumulative distribution function of a standard normal random variable.

    Implementation is a quadratic approximation with modest accuracy over [-4, 4].
    """
    A = scipy.sparse.diags(
        np.sqrt(
            [
                0.02301291,
                0.08070214,
                0.16411522,
                0.09003495,
                0.08200854,
                0.01371543,
                0.04641081,
            ]
        )
    )
    b = np.array([[3.0, 2.0, 1.0, 0.0, -1.0, -2.5, -3.5]]).reshape(-1, 1)

    is_scalar = not hasattr(x, "shape")
    if is_scalar or not x.shape:
        x_size = 1
    else:
        x_size = functools.reduce(lambda i, j: i * j, x.shape)

    flat_x = reshape(x, (1, x_size))

    y = A @ (b @ np.ones(flat_x.shape) - np.ones(b.shape) @ flat_x)
    out = -sum_(maximum(y, 0) ** 2, axis=0)

    if is_scalar:
        return out[0]
    else:
        return reshape(out, x.shape)
