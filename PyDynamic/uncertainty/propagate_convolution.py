# -*- coding: utf-8 -*-
"""
The convolution operation is a common operation in signal and data
processing. Convolving signals is mathematically similar to a filter
application. 

This module contains the following function:
* :func:`convolve_unc`: Convolution with uncertainty propagation based on FIR-filter
"""

import numpy as np

from .propagate_filter import _fir_filter

__all__ = ["convolve_unc"]


def convolve_unc(x1, U1, x2, U2, mode="full"):
    """
    An implementation of the discrete convolution of two signals with uncertainty propagation.
    The code builds on PyDynamic.uncertainty._fir_filter, as convolution and filter application
    are mathematically nearly identical. However, boundary effects need to be taken into account.

    Parameters
    ----------
    x1 : np.ndarray, (N,)
        first input signal
    U1 : np.ndarray, (N, N)
        full 2D-covariance matrix associated with x1
        if the signal is fully certain, use `U1 = None` to make use of more efficient calculations.
    x2 : np.ndarray, (M,)
        second input signal
    U2 : np.ndarray, (M, M)
        full 2D-covariance matrix associated with x2
        if the signal is fully certain, use `U2 = None` to make use of more efficient calculations.
    mode : str, optional
        :func:`numpy.convolve`-modes:

        - full:  len(y) == N+M-1 (default)
        - valid: len(y) == max(M, N) - min(M, N) + 1
        - same:  len(y) == max(M, N) (value+covariance are padded with zeros)
        
        :func:`scipy.ndimage.convolve1d`-modes:

        - nearest: len(y) == N (value+covariance are padded with by stationary assumption)
        - reflect:  len(y) == N
        - mirror:   len(y) == N

    Returns
    -------
    y : np.ndarray
        convoluted output signal
    Uy : np.ndarray
        full 2D-covariance matrix of y

    References
    ----------
    .. seealso::
        :func:`numpy.convolve`
        :func:`scipy.ndimage.convolve1d`
        :func:`PyDynamic.uncertainty.propagate_filter._fir_filter`
    """

    # if a numpy-mode is chosen, x1 is expected to be the longer signal
    # remember that pure convolution is commutative
    if len(x1) < len(x2) and mode in ["valid", "full", "same"]:
        tmp = x1
        x1 = x2
        x2 = tmp

        tmp = U1
        U1 = U2
        U2 = tmp

    # actual computation
    if mode == "valid":
        # apply _fir_filter directly
        y, Uy = _fir_filter(x=x1, theta=x2, Ux=U1, Utheta=U2, initial_conditions="zero")

        # remove first len(x2)-1 entries from output
        conv = y[len(x2) - 1 :]
        Uconv = Uy[len(x2) - 1 :, len(x2) - 1 :]

    elif mode == "full":
        # append len(b)-1 zeros to x1/U1
        pad_len = len(x2) - 1
        x1_mod = np.pad(x1, (0, pad_len), mode="constant", constant_values=0)
        if isinstance(U1, np.ndarray):
            U1_mod = np.pad(
                U1, ((0, pad_len), (0, pad_len)), mode="constant", constant_values=0
            )
        else:
            U1_mod = None

        # apply _fir_filter
        y, Uy = _fir_filter(
            x=x1_mod, theta=x2, Ux=U1_mod, Utheta=U2, initial_conditions="zero"
        )

        # use output directly
        conv = y
        Uconv = Uy

    elif mode == "same":
        # append (len(x2)-1)//2 to x1
        pad_len = (len(x2) - 1) // 2
        x1_mod = np.pad(x1, (0, pad_len), mode="constant", constant_values=0)
        if isinstance(U1, np.ndarray):
            U1_mod = np.pad(
                U1, ((0, pad_len), (0, pad_len)), mode="constant", constant_values=0
            )
        else:
            U1_mod = None

        # apply _fir_filter
        y, Uy = _fir_filter(
            x=x1_mod, theta=x2, Ux=U1_mod, Utheta=U2, initial_conditions="zero"
        )

        # remove first (len(x2)-1)//2 entries from output
        conv = y[pad_len:]
        Uconv = Uy[pad_len:, pad_len:]

    elif mode in ["nearest", "reflect", "mirror"]:

        # scipy.ndimage.convolve1d and numpy.pad use different (but overlapping) terminology
        mode_translation = {
            "nearest": "edge",
            "reflect": "symmetric",
            "mirror": "reflect",
        }
        pad_mode = mode_translation[mode]

        # append (len(x2)-1)//2 to x1
        n1 = len(x1)
        n2 = len(x2)
        pad_len = (n2 + 1) // 2
        x1_mod = np.pad(x1, (pad_len, pad_len), mode=pad_mode)
        # only append, if U is an array (leave it as None)
        if isinstance(U1, np.ndarray):
            U1_mod = np.pad(U1, ((pad_len, pad_len), (pad_len, pad_len)), mode=pad_mode)
        else:
            U1_mod = None

        # apply _fir_filter
        y, Uy = _fir_filter(
            x=x1_mod, theta=x2, Ux=U1_mod, Utheta=U2, initial_conditions="zero"
        )

        # remove leading and trailing entries from output
        conv = y[n2 : n2 + n1]
        Uconv = Uy[n2 : n2 + n1, n2 : n2 + n1]

    else:
        raise ValueError(
            'convolve_unc: Mode "{MODE}" is not supported.'.format(MODE=mode)
        )

    return conv, Uconv
