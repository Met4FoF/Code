# -*- coding: utf-8 -*-
"""The module :mod:`PyDynamic.identification.fit_transfer` contains several functions
for the identification of transfer function models.

This module contains the following function:

* :func:`fit_sos`: Fit second-order model to complex-valued frequency response


.. deprecated:: 1.2.71
    The package *identification* will be combined with the package *deconvolution* and
    renamed to *model_estimation* in the next major release 2.0.0. From version 1.4.1 on
    you should only use the new package *model_estimation* instead.
"""
import warnings

import numpy as np

from ..model_estimation.fit_transfer import fit_sos

__all__ = ["fit_sos"]

warnings.simplefilter("default")
warnings.warn(
    "The package *identification* will be combined with the package "
    "*deconvolution* and renamed to *model_estimation* in the "
    "next major release 2.0.0. From version 1.4.1 on you should only use "
    "the new package *model_estimation* instead.",
    DeprecationWarning,
)
