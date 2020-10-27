# -*- coding: utf-8 -*-
"""
.. deprecated:: 2.0.0
    The module :mod:`PyDynamic.uncertainty.interpolation` is renamed to
    :mod:`PyDynamic.uncertainty.interpolate` since the last major release 2.0.0. It
    might be removed any time. Please switch to the current module immediately.
"""
import warnings

from .interpolate import interp1d_unc

__all__ = ["interp1d_unc"]

warnings.simplefilter("default")
warnings.warn(
    "The module :mod:`PyDynamic.uncertainty.interpolation` is renamed to "
    ":mod:`PyDynamic.uncertainty.interpolate` since the last major release 2.0.0. "
    "Please switch to the current module immediately.",
    DeprecationWarning,
)
