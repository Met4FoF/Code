"""This module implements the signals class and its derivatives

Signals are dynamic quantities with associated uncertainties. A signal has to be defined
together with a time axis.

.. note:: This module is experimental!
"""

__all__ = ["Signal"]

import numpy as np
from matplotlib.pyplot import figure, fill_between, legend, plot, xlabel, ylabel

from .misc.tools import (
    is_2d_matrix,
    is_2d_square_matrix,
    number_of_rows_equals_vector_dim,
)
from .uncertainty.propagate_filter import FIRuncFilter
from .uncertainty.propagate_MonteCarlo import MC


class Signal:
    """The base class which defines the interfaces and default behaviour."""

    unit_time = ""
    unit_values = ""
    name = ""

    def __init__(self, time, values, Ts=None, Fs=None, uncertainty=None):
        if len(values.shape) > 1:
            raise NotImplementedError(
                "Signal: Multivariate signals are not implemented yet."
            )
        assert len(time) == len(values)
        self.time = time
        self.values = values
        # set sampling interval and frequency
        if (Ts is None) and (Fs is None):
            self.Ts = np.unique(np.diff(self.time)).mean()
            self.Fs = 1 / self.Ts
        elif isinstance(Ts, float):
            self.Ts = Ts
            if Fs is None:
                self.Fs = 1 / Ts
            elif not np.allclose(Fs, np.reciprocal(self.Ts)):
                raise ValueError(
                    "Signal: Sampling interval and sampling frequency are assumed to "
                    "be approximately multiplicative inverse to each other, but "
                    f"Fs={Fs} and Ts={Ts}. Please adjust either one of them."
                )
        # set initial uncertainty
        if isinstance(uncertainty, float):
            self.uncertainty = np.ones_like(values) * uncertainty
            self.uncertainty_main_diagonal = self.uncertainty
        elif isinstance(uncertainty, np.ndarray):
            uncertainty = uncertainty.squeeze()
            if not number_of_rows_equals_vector_dim(matrix=uncertainty, vector=time):
                raise ValueError(
                    "Signal: if uncertainties are provided as np.ndarray "
                    f"they are expected to match the number of elements of the "
                    f"provided time vector, but uncertainties are of shape "
                    f"{uncertainty.shape} and time is of length {len(time)}. Please "
                    f"adjust either one of them."
                )
            if is_2d_matrix(uncertainty) and not is_2d_square_matrix(uncertainty):
                raise ValueError(
                    "Signal: if uncertainties are provided as 2-dimensional np.ndarray "
                    f"they are expected to resemble a square matrix, but uncertainties "
                    f"are of shape {uncertainty.shape}. Please "
                    f"adjust them."
                )
            self.uncertainty = uncertainty
            self.uncertainty_main_diagonal = np.diag(self.uncertainty)
        else:
            self.uncertainty = np.zeros_like(values)
            self.uncertainty_main_diagonal = self.uncertainty
        self.set_labels()

    def set_labels(self, unit_time="s", unit_values="a.u.", name_values="signal"):
        self.unit_time = unit_time
        self.unit_values = unit_values
        self.name = name_values

    def plot(self, fignr=1, figsize=(10, 8)):
        figure(fignr, figsize=figsize)
        plot(self.time, self.values, label=self.name)
        fill_between(
            self.time,
            self.values - self.uncertainty_main_diagonal,
            self.values + self.uncertainty_main_diagonal,
            color="gray",
            alpha=0.2,
        )
        xlabel("time / %s" % self.unit_time)
        ylabel("%s / %s" % (self.name, self.unit_values))
        legend(loc="best")

    def plot_uncertainty(self, fignr=2, **kwargs):
        figure(fignr, **kwargs)
        plot(
            self.time,
            self.uncertainty_main_diagonal,
            label="uncertainty associated with %s" % self.name,
        )
        xlabel("time / %s" % self.unit_time)
        ylabel("uncertainty / %s" % self.unit_values)
        legend(loc="best")

    def apply_filter(self, b, a=1, filter_uncertainty=None, MonteCarloRuns=None):
        """Apply digital filter (b, a) to the signal values

        Apply digital filter (b, a) to the signal values and propagate the
        uncertainty associated with the signal.

        Parameters
        ----------
        b : np.ndarray
            filter numerator coefficients
        a : np.ndarray
            filter denominator coefficients, use a=1 for FIR-type filter
        filter_uncertainty : np.ndarray
            covariance matrix associated with filter coefficients,
            Uab=None if no uncertainty associated with filter
        MonteCarloRuns : int
            number of Monte Carlo runs, if `None` then GUM linearization
            will be used
        """

        if isinstance(a, list):
            a = np.array(a)
        if not (isinstance(a, np.ndarray)):  # FIR type filter
            if len(self.uncertainty.shape) == 1:
                if not isinstance(MonteCarloRuns, int):
                    self.values, self.uncertainty = FIRuncFilter(
                        self.values, self.uncertainty, b, Utheta=filter_uncertainty
                    )
                else:
                    self.values, self.uncertainty = MC(
                        self.values,
                        self.uncertainty,
                        b,
                        a,
                        filter_uncertainty,
                        runs=MonteCarloRuns,
                    )
            else:
                if not isinstance(MonteCarloRuns, int):
                    MonteCarloRuns = 10000
                self.values, self.uncertainty = MC(
                    self.values,
                    self.uncertainty,
                    b,
                    a,
                    filter_uncertainty,
                    runs=MonteCarloRuns,
                )
        else:  # IIR-type filter
            if not isinstance(MonteCarloRuns, int):
                MonteCarloRuns = 10000
                self.values, self.uncertainty = MC(
                    self.values,
                    self.uncertainty,
                    b,
                    a,
                    filter_uncertainty,
                    runs=MonteCarloRuns,
                )
