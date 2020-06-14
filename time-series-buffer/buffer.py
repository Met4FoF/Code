from collections import deque

import numpy as np
from uncertainties import unumpy


__all__ = ["TimeSeriesBuffer"]

class TimeSeriesBuffer:
    """
    Custom buffer class, that allows to save streams of time-series with uncertainty 
    in timestamps and values. Acts like a FIFO buffer.
    """

    empty_value = np.nan
    empty_unc = 0.0  # np.nan?
    supported_iterable_types = [list, tuple, np.ndarray]

    def __init__(self, maxlen=10, return_type="array"):
        """Initialize a FIFO buffer.
        
        Parameters
        ----------
            maxlen: int (default: 10)
                maximum length of the buffer, directly handed over to deque

            return_type: str (default: array)

                * list: return data as list of tuples of (time, time_unc, val, val_unc)
                * array: float-array of shape (N, 4) where rows correspond to (time, time_unc, val, val_unc)
                * uarray: ufloat-array of shape (N, 2) where rows correspond to (time, val)
                * arrays: four float-arrays of shape (N, 1)
                * uarrays: two ufloat-arrays of shape (N, 1)
        
        """
        self.buffer = deque(maxlen=maxlen)
        self.return_type = return_type

    def __len__(self):
        return len(self.buffer)

    def add(self, data=None, time=self.empty_value, time_unc=self.empty_unc, val=self.empty_value, val_unc=self.empty_unc):
        """Append one or more new datapoints to the buffer. 
        A datapoint consists of the tuple (time, time_uncertainty, value, value_uncertainty).
        
        Parameters
        ----------
            data: iterable of iterables with shape (N, M) (default: None)
                If given, all other kwargs are ignored.
                
                * M==2 (pairs): assumed to be like (time, value)
                * M==3 (triple): assumed to be like (time, value, value_unc)
                * M==4 (4-tuple): assumed to be like (time, time_unc, value, value_unc)

            time: float, or iterable of float/ufloat (default: np.nan)
                Timestamp(s) to be added.

            time_unc: float, or iterable of float (default: 0.0)
                Uncertainty(ies) of the timestamp(s) to be added.

            val: (iterable of) float/ufloat (default: np.nan)
                Value(s) to be added.

            val_unc: (iterable of) float (default: 0.0)
                Uncertainty(ies) of the value(s) to be added.
    
            time, time_unc, val, val_unc need to be of same shape, but uncertainties can be omitted. 
        
        """

        # time series is given as iterable of iterables
        if isinstance(data, self.supported_iterable_types):

            for datapoint in data:
                t = self.empty_value
                ut = self.empty_unc
                v = self.empty_value
                uv = self.empty_unc

                # datapoint is a pair, could be pair of float or pair of ufloat
                if len(datapoint) == 2:
                    if isinstance(datapoint[0], uncertainties.core.Variable):
                        t = datapoint[0].nominal_value
                        ut = datapoint[0].std_dev
                    else:
                        t = datapoint[0]

                    if isinstance(datapoint[1], uncertainties.core.Variable):
                        v = datapoint[1].nominal_value
                        uv = datapoint[1].std_dev
                    else:
                        v = datapoint[1]

                # datapoint is a triple
                elif len(datapoint) == 3:  # triple
                    t = datapoint[0]
                    v = datapoint[1]
                    uv = datapoint[2]

                elif len(datapoint) == 4:  # 4-tuple
                    t = datapoint[0]
                    ut = datapoint[1]
                    v = datapoint[2]
                    uv = datapoint[3]

                self.buffer.append((t, ut, v, uv))

        # time series is given as iterable of floats
        elif isinstance(time, self.supported_iterable_types):
            # time
            t = time

            # time uncertainty (could be array of same shape as time, single float or None)
            if isinstance(time_unc, self.supported_iterable_types):
                ut = time_unc
            else:
                ut = [time_unc] * len(time)

            # value (could be array of same shape as time, single float or None)
            if isinstance(val, self.supported_iterable_types):
                v = val
            else:
                v = [val] * len(time)

            # value uncertainty (could be array of same shape as time, single float or None)
            if isinstance(val_unc, self.supported_iterable_types):
                uv = val_unc
            else:
                uv = [val_unc] * len(time)

            for datapoint in zip(t, ut, v, uv):
                self.buffer.append(datapoint)
        
        elif isinstance(time, float):
            self.buffer.append((time, time_unc, val, val_unc))

        else:
            raise ValueError("Your provided type for data or time is not supported.")

    def pop(self, n_samples=1):
        """
        Return the next `n_samples` from the left side of the buffer.

        View the latest `n` additions to the buffer. Returns the format that
        was specified during init of the buffer.
        
        Parameters
        ----------
            n: int (default: 1)
                How many datapoints to return.
        
        Return
        ------
            Depends on return_type, see :py:func:`show` for details?
        """

        # take the next samples from the beginning of buffer
        n_pop = min(n_samples, len(self.buffer))
        next_samples = [self.buffer.popleft() for i in range(n_pop)]

        # return as specified
        return self._return_converter(next_samples)

    def show(self, n_samples=1):
        """
        View the latest `n_samples` additions to the buffer. Returns the format that
        was specified during init of the buffer.
        """

        # take the next samples from the beginning of buffer
        n_buffer = len(self.buffer)
        n_pop = min(n_samples, n_buffer)
        next_samples = [self.buffer[n_buffer - (i + 1)] for i in range(n_pop)]

        # return as specified
        return self._return_converter(next_samples)

    def _return_converter(self, samples):
        
        if self.return_type == "list":
            return samples

        else:
            data = np.array(samples)
            t = data[:,0]
            ut = data[:,1]
            v = data[:,2]
            uv = data[:,3]

            if self.return_type == "array":
                return np.vstack(data)

            elif self.return_type == "arrays":
                return t, ut, v, uv

            elif self.return_type == "uarray":
                tt = unumpy.uarray(t, ut)
                vv = unumpy.uarray(v, uv)

                return np.vstack(tt,vv).T

            elif self.return_type == "uarrays":
                tt = unumpy.uarray(t, ut)
                vv = unumpy.uarray(v, uv)

                return tt, vv

