from typing import Optional

import numpy as np
from scipy.interpolate import interp1d


def interp1d_unc(t_new, t, y, uy, kind: Optional[str] = "linear"):
    """Interpolate arbitrary time series considering the associated uncertainties

    Parameters
    ----------
        t_new: np.ndarray
            (N,) The timestamps at which to evaluate the interpolated values.
        t: np.ndarray
            (N,) timestamps in ascending order
        y: np.ndarray
            (N,) corresponding measurement values
        uy: np.ndarray
            (N,) corresponding measurement values' uncertainties
        kind: str
            Specifies the kind of interpolation for the measurement values
            as a string ('previous', 'next', 'nearest' or 'linear').

    Returns
    -------
        t_new : (N,) array_like
            timestamps
        y_new : (N,) array_like
            measurement values
        uy_new : (N,) array_like
            measurement values' uncertainties

    References
    ----------
        * White [White2017]_
    """
    # Cover the case where
    # Check for ascending order of timestamps.
    if not np.all(t[1:] >= t[:-1]):
        raise ValueError("Array of timestamps needs to be in ascending order.")
    # Setup new vectors of timestamps.
    # Interpolate measurement values in the desired fashion.
    interp_y = interp1d(t, y, kind=kind)
    y_new = interp_y(t_new)

    if kind in ("previous", "next", "nearest"):
        # Look up uncertainties in cases where it is applicable.
        interp_uy = interp1d(t, uy, kind=kind)
        uy_new = interp_uy(t_new)
    else:
        if kind == "linear":
            # Determine the relevant interpolation intervals for all new timestamps.
            # We determine the intervals for each timestamp in t_new by finding the
            # biggest of all timestamps in t smaller or equal than the one in t_new.
            # If the maximums are equal we manually choose the last two
            # timestamps in t as interval bounds, since our algorithm results in two
            # times the last timestamp in t.
            indices = np.empty_like(t_new, dtype=int)
            it_t_new = np.nditer(t_new, flags=["f_index"])
            while not it_t_new.finished:
                # Find indices of biggest of all timestamps smaller or equal
                # than current time, assumes that timestamps are in ascending
                # order.
                indices[it_t_new.index] = np.where(t <= it_t_new[0])[0][-1]
                it_t_new.iternext()
            # Correct the last interval in case it degenerated. This happens when the
            # last timestamps of t and t_new are equal.
            if indices[-1] == len(t) - 1:
                indices[-1] -= 1
            t_prev = t[indices]
            t_next = t[indices + 1]
            # Look up corresponding input uncertainties.
            uy_prev_sqr = uy[indices] ** 2
            uy_next_sqr = uy[indices + 1] ** 2
            # Compute uncertainties for interpolated measurement values.
            uy_new = np.sqrt(
                (t_new - t_next) ** 2 * uy_prev_sqr
                + (t_new - t_prev) ** 2 * uy_next_sqr
            ) / (t_next - t_prev)
        else:
            raise NotImplementedError

    return t_new, y_new, uy_new
