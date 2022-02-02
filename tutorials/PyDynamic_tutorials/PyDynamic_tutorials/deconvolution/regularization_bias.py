"""Functions for the estimation of the regularization error and its unc. contribution"""
import numpy as np
import scipy.signal as dsp


def calculate_freq_points(fH, H, X, Fs, candidates, verbose=True):
    def get_candidates(f, S, number=40):
        # Largest local maxima of np.abs(S)
        inds = dsp.argrelmax(np.abs(S))[0]
        inds2 = inds[np.argsort(np.abs(S[inds]))[::-1]]
        return f[inds2[:number]], inds2[:number], np.abs(S[inds2[:number]])

    def get_closest(freqs, f_localmax):
        # Closest local maximum to selected frequency
        cfreqs = freqs.copy()
        for k in range(len(freqs)):
            indf = np.argmin(np.abs(f_localmax - freqs[k]))
            cfreqs[k] = f_localmax[indf]
        return cfreqs

    Nf = 2 * (len(fH) - 1)
    Ts = 1 / Fs
    f = np.fft.rfftfreq(Nf, Ts)

    Xh = X / H

    f_local = get_candidates(fH, np.abs(Xh))[0]
    frequencies = get_closest(candidates, f_local)

    return frequencies


def calculate_bound_from_measurement(
    fH, FR, meas, freq_points, scale=True, verbose=True, Fs=500e6
):
    """Calculate the bound function from the measured signal and the measuring instrument's frequency response

    Parameters
    ----------
        fH : np.ndarray
             frequencies at which the frequency response is defined
        FR : np.ndarray of dtype complex
             complex-valued hydrophone frequency response
        meas : np.ndarray
             time domain measurement signal
        freq_points : list
             frequencies at which the Gaussian wavelets are centered

    Returns
    -------
        B : np.ndarray of shape (N,), spectrum of bound
        spectra : np.narray of shape (K,N) with amplitude of the spectrum of the K wavelets
        Xh : np.ndarray of shape (N,), spectrum of unregularized estimate of measurand

    """

    def psihat(A, sigma):
        # Gaussian wavelet spectrum
        return (
            lambda f: A
            * np.exp(0.5)
            * sigma
            * (2 * np.pi * f)
            * np.exp(-0.5 * sigma**2 * (2 * np.pi * f) ** 2)
        )

    def freq2scale(f):
        # Calculation of wavelet scale from center frequency
        return 1 / (2 * np.pi * f)

    def get_amplitude(Amps, freqs, fv):
        ind1 = np.nonzero(freqs <= fv)[0][-1]
        ind2 = ind1 + 1
        f1, A1 = freqs[ind1], Amps[ind1]
        f2, A2 = freqs[ind2], Amps[ind2]
        return (A2 - A1) / (f2 - f1) * (fv - f1) + A1

    Nf = 2 * (len(fH) - 1)
    Ts = 1 / Fs
    f = np.fft.rfftfreq(Nf, Ts)

    if len(meas) == Nf:
        X = np.fft.rfft(meas)
    else:
        if verbose:
            print(
                "The length of the measured signal does not fit the length of the hydrophone frequency response.\nDoing zero-padding to this end."
            )
        X = np.fft.rfft(np.r_[meas, np.zeros(Nf - len(meas))])
    Xh = X / FR

    sigma_vals = [freq2scale(ff) for ff in freq_points]
    Mvals = [get_amplitude(np.abs(Xh), fH, ff) for ff in freq_points]
    amplitude_vals = Mvals

    if verbose:
        for fv, sv, av in zip(freq_points, sigma_vals, amplitude_vals):
            print("characterising frequency: %g MHz" % (fv * 1e-6), end="")
            print(" corresponding sigma: %g" % (sv), end="")
            print(" and amplitude %g" % av)

    freq_funcs = [psihat(A, sigma) for A, sigma in zip(amplitude_vals, sigma_vals)]
    spectra = np.r_[[freq_funcs[k](f) for k in range(len(freq_points))]]

    B = spectra.sum(axis=0) / Fs
    if scale:
        B *= np.abs(Xh).max() / Fs / B.max()

    return B, spectra * Ts, Xh


def calc_bound_value(B, G, H, f, Fs):
    """
    Calculation of the upper bound on the dynamic error in the time domain from an upper bound in the frequency domain.

    Parameters
    ----------
        B : np.ndarry of shape (M,) or lambda function with argument f
            upper bound in amplitude spectrum
        G : np.ndarray of shape (M,)
            frequency response of applied deconvolution filter at frequencies f
        H : np.ndarray of shape (M,) or lambda function with argument f
            frequency response of measurement system
        f : np.ndarray
            frequencies
        Fs: float
            sampling frequency

    Returns
    -------
        float
        upper bound of dynamic error
    """

    if not isinstance(B, np.ndarray):
        boundFreq = B(f)
    else:
        boundFreq = B
    if not isinstance(H, np.ndarray):
        system = H(f)
    else:
        system = H

    freq_devs = boundFreq * np.abs(G * system - 1)
    return 1 / (2 * np.pi) * np.trapz(freq_devs, f)
