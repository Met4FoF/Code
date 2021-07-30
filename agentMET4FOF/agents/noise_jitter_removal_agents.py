import math
import numpy as np
import numpy.matlib
from scipy.optimize import minimize

from agentMET4FOF.agents import AgentMET4FOF

"""### mcmcci: MCMC convergence indices for multiple chains."""

def mcmcci(A,M0):
    '''
    mcmcci: MCMC convergence indices for multiple chains.
    ----------------------------------------------------------------------------
    KJ, LRW, PMH

    Version 2020-04-22

    ----------------------------------------------------------------------------
    Inputs:
    A(M, N): Chain samples, N chains of length M.

    M0: Length of burn-in, M > M0 >= 0.

    Outputs:
    Rhat: Convergence index. Rhat is expected to be greater than 1. The closer
    Rhat is to 1, the better the convergence.

    Neff: Estimate of the effective number of independent draws. Neff is
    expected to be less than (M-M0)*N.
    ----------------------------------------------------------------------------
    Note: If the calculated value of Rhat is < 1, then Rhat is set to 1 and Neff
    set to (M-M0)*N, their limit values.

    Note: If N = 1 or M0 > M-2, Rhat = 0; Neff = 0.
    '''
    A = np.array(A)

    M, N = A.shape

    # Initialisation
    Rhat = 0
    Neff = 0

    # The convergence statistics can only be evaluated if there are multiple chains
    # and the chain length is greater than the burn in length

    if N > 1 and M > M0 + 1:
        Mt = M - M0

        # Chain mean and mean of means
        asub = A[M0:,:]
        ad = np.mean(asub,axis = 0)
        add = asub.mean()

        # Within group standard deviation
        ss = np.std(asub,axis = 0)

        # Between groups variance.
        dd = np.square(ad - add)
        B = (Mt*np.sum(dd))/(N-1)

        # Within groups variance.
        W = np.sum(np.square(ss))/N

        # V plus
        Vp = (Mt-1)*W/Mt + B/Mt

        # Convergence statistic, effective number of independent samples
        Rhat = np.sqrt(Vp/W)
        Neff = Mt*N*Vp/B

        Rhat = np.maximum(Rhat,1)
        Neff = np.minimum(Neff,Mt*N)

    return Rhat, Neff

"""### mcsums: Summary information from MC samples."""

def mcsums(A,M0,Q):
    '''
    mcsums: Summary information from MC samples.
    -------------------------------------------------------------------------
    KJ, LRW, PMH
    Version 2020-04-22

    -------------------------------------------------------------------------
    Inputs:
    A(M,N): An array that stores samples of size M x N.

    M0: Burn-in period with M > M0 >= 0.

    Q(nQ,1): Percentiles specifications, 0 <= Q(l) <= 100.

    Outputs:
    abar(n,1): Mean for each sample.

    s(n,1): Standard deviation for sample.

    aQ(nQ,n): Percentiles corresponding to Q.

    '''
    # Size of samples after burn-in
    A = np.array(A)

    M, N = A.shape

    m = (M - M0)*N

    # Initialise percentile vector
    nQ = Q.size
    aQ = np.zeros(nQ)

    # Samples from N parallel chains after burn-in period
    aaj = A[M0:, :]
    aaj = aaj.flatten()

    # Mean and standard deviation of samples
    abar = np.mean(aaj)
    s = np.std(aaj)

    # Percentiles of samples
    aQ = np.percentile(aaj,Q)

    return abar, s, aQ

"""### jumprwg: Jumping distribution for the Metropolis Hastings Gaussian random walk algorithm"""

def jumprwg(A, L):
    '''
    jumprwg: Jumping distribution for the Metropolis Hastings Gaussian random
    walk algorithm
    -------------------------------------------------------------------------
    KJ, LRW, PMH
    Version 2020-04-22
    -------------------------------------------------------------------------
    Inputs:
    A(n,N): Samples at the current iteration

    L(n,n): Cholesky factor of variance of parameter vector.

    Outputs:
    As(n,N): Proposed parameter array which is randomly sampled from the
    jumping distribution

    dp0: The difference between the logarithm of the jumping distribution
    associated with moving from A(:,j) to As(:,j) and that associated with
    moving from As(:,j) to A(:,j), up to an additive constant.
    log P0(a|as) - log P0(as|a)

    '''
    # Number of parameters and parallel chains
    n, N = A.shape

    # random draw from a Gaussian distribution
    e = np.random.normal(0, 1, size=(n,N))

    # proposed draw from a Gaussian distribution with mean A and variance LL'
    As = A + np.matmul(L,e)

    # For a Gaussian random walk, since log P0(a|as) = log P0(as|a), dp0 will always be zero
    dp0 = np.zeros(N)

    return As, dp0

"""### Cubic function and its first and second derivative"""

def fgh_cubic(alpha,t):
    '''
    -------------------------------------------------------------------------
    Cubic function and its first and second derivative
    -------------------------------------------------------------------------
    KJ, LRW, PMH
    Version 2020-04-22
    -------------------------------------------------------------------------
    Inputs:
    alpha(4,N):             Alpha parameters

    t(m,1):                 Times

    Outputs:
    f(m,N):                 Cubic function

    f1(m,N):                Derivative of cubic

    f2(m,N):                Second derivative of cubic
    '''

    # length of data and number of paramaters
    m = t.size

    # design matrix
    C = np.array([np.ones(m), t, t**2, t**3])

    # derivate info
    C1 = np.array([np.ones(m), 2*t, 3*t**2])
    C2 = np.array([2*np.ones(m), 6*t])

    # cubic and derivatives
    f = np.matmul(C.T,alpha)
    f1 = np.matmul(C1.T,alpha[1:])
    f2 = np.matmul(C2.T,alpha[2:])

    return f, f1, f2

"""### Log of the gaussian pdf"""

def ln_gauss_pdf_v(x,mu,sigma):
    '''
    -------------------------------------------------------------------------
    Log of the Gaussian pdf
    -------------------------------------------------------------------------
    KJ, LRW, PMH
    Version 2020-03-12
    --------------------------------------------------------------------------
    Inputs:
    x(m,1):                 Points at which pdf is to be evaluated

    mu:                     Mean of distribution

    sigma:                  Standard deviation of the distribution

    Output:
    logf:                   Log of the Gaussian pdf at x with mean mu and
                            std sigma
    '''


    try:
      # When inputs are high dimensional arrays/matrices
      xx = np.matlib.repmat(x,mu.shape[1],1)
      xx = xx.T
      logk = - np.log(2*math.pi)/2 - np.log(sigma)
      logp = -((xx - mu)**2)/(2*sigma**2)
      # Log of the Gaussian PDF
      logf = logk + logp

    except IndexError:
      # When inputs are vectors
      logk = - np.log(2*math.pi)/2 - np.log(sigma)
      logp = -((x - mu)**2)/(2*sigma**2)
      # Log of the Gaussian PDF
      logf = logk + logp

    return logf

"""### Target dist for noise and jitter posterior dist"""

def tar_at(at, y, x, m0w, s0w, m0t, s0t):
    '''
    -------------------------------------------------------------------------
    Target dist for noise and jitter posterior dist
    -------------------------------------------------------------------------
    KJ, LRW, PMH
    Version 2020-04-22
    --------------------------------------------------------------------------
    Inputs:
    at(n+2,N):              Parameters alpha, log(1/tau^2) and log(1/w^2)

    y(m,1):                 Signal

    x(m,1):                 time at which signal was recorded

    s0w and s0t:            prior estimates of tau and omega

    m0w and m0t:            degree of belief in prior estimates for tau and omega

    Output:
    T:                      Log of the posterior distribution
    '''

    # Size of parameter vector
    at = np.array(at)
    p = at.shape[0]

    # Number of alphas
    n = p - 2

    # Extract parameters
    alpha = at[0:n]
    phi1 = np.exp(at[-2])
    phi2 = np.exp(at[-1])
    taus = np.ones(phi1.shape)/np.sqrt(phi1)
    omegas = np.ones(phi2.shape)/np.sqrt(phi2)

    # Gamma priors for phis
    prior_phi1 = (m0t/2)*np.log(phi1) - phi1*m0t*s0t**2/2
    prior_phi2 = (m0w/2)*np.log(phi2) - phi2*m0w*s0w**2/2


    # function that evaluates the cubic function with user specified cubic parameters
    fun = lambda aa: fgh_cubic(aa, x)

    # cubic, expectation and variance
    [st,st1,st2] = fun(alpha)
    expect = st + 0.5*(taus**2)*st2
    vari = (taus**2)*(st1**2) + omegas**2

    # Likelihood
    lik = sum(ln_gauss_pdf_v(y,expect,np.sqrt(vari)))

    # Posterior
    T = lik + prior_phi1 + prior_phi2

    return T

"""###mcmcmh: Metrolopolis-Hasting MCMC algorithm generating N chains of length M for a parameter vector A of length n."""

def mcmcmh(M, N, M0, Q, A0, tar, jump):
    '''
    mcmcmh: Metrolopolis-Hasting MCMC algorithm generating N chains of length
    M for a parameter vector A of length n.

    For details about the algorithm please refer to:
    Gelman A, Carlin JB, Stern HS, Dunson DB, Vehtari A, Rubin DB.
    Bayesian data analysis. CRC press; 2013 Nov 1.
    -------------------------------------------------------------------------
    KJ, LRW, PMH
    Version 2020-04-22
    -------------------------------------------------------------------------
    Inputs:
    M: Length of the chains.

    N: Number of chains.

    M0: Burn in period.

    Q(nQ,1): Percentiles 0 <= Q(k) <= 100.

    A0(n,N): Array of feasible starting points: the target distribution
    evaluated at A0(:,j) is strictly positive.

    Outputs:

    S(2+nQ,n): Summary of A - mean, standard deviation and percentile limits,
    where the percentile limits are given by Q.

    aP(N,1): Acceptance percentages for AA calculated for each chain.

    Rh(n,1): Estimate of convergence. Theoretically Rh >= 1, and the closer
    to 1, the more evidence of convergence.

    Ne(n,1): Estimate of the number of effective number of independent draws.

    AA(M,N,n): Array storing the chains: A(i,j,k) is the kth element of the
    parameter vector stored as the ith member of the jth chain.
    AA(1,j,:) = A0(:,j).

    IAA(M,N): Acceptance indices. IAA(i,j) = 1 means that the proposal
    as(n,1) generated at the ith step of the jth chain was accepted so
    that AA(i,j,:) = as. IAA(i,j) = 0 means that the proposal as(n,1)
    generated at the ith step of the jth chain was rejected so that
    AA(i,j,:) = AA(i-1,j,:), i > 1. The first set of proposal coincide with
    A0 are all accepted, so IAA(1,j) = 1.
    '''
    A0 = np.array(A0)
    Q = np.array(Q)
    # number of parameters for which samples are to be drawn
    n = A0.shape[0]

    # number of percentiles to be evaluated
    nQ = Q.size


    # Initialising output arrays
    AA = np.empty((M, N, n))
    IAA = np.zeros((M, N))
    Rh = np.empty((n))
    Ne = np.empty((n))
    S = np.empty((2 + nQ, n))


    # starting values of the sample and associated log of target density
    aq = A0
    lq = tar(aq)

    # Starting values must be feasible for each chain
    Id = lq > -np.Inf

    if sum(Id) < N:
        print("Initial values must be feasible for all chains")
        return None


    # Run the chains in parallel
    for q in range(M):
        # draw from the jumping distribution and calculate
        # d = log P0(aq|as) - log P0(as|aq)

        asam, d = jump(aq)

        # log of the target density for the new draw as
        ls = tar(asam)

        # Metropolis-Hastings acceptance ratio
        rq = np.exp(ls - lq + d)

        # draws from the uniform distribution for acceptance rule
        uq = np.random.rand(N)
        # index of samples that have been accepted
        ind = uq < rq

        # updating the sample and evaluating acceptance indices
        aq[:, ind] = asam[:, ind]
        lq[ind] = ls[ind]
        IAA[q, ind] = 1

        # Store Metropolis Hastings sample
        AA[q, :, :] = np.transpose(aq)


    # acceptance probabilities for each chain
    aP = 100*np.sum(IAA,0)/M

    # Convergence and summary statistics for each of the n parameters
    for j in range(n):
        # test convergence
        RN = mcmcci(np.squeeze(AA[:,:,j]), M0)
        Rh[j] = RN[0]
        Ne[j] = RN[1]

        # provide summary information
        asq = np.squeeze(AA[:,:,j])
        SS = mcsums(asq,M0,Q)
        S[0,j] = SS[0]
        S[1,j] = SS[1]
        S[2:,j] = SS[2]

    return S, aP, Rh, Ne, AA, IAA

def mcmcm_main(datay, datax, m0w, s0w, m0t, s0t, Mc, M0, Nc, Q):

  at0 = np.array((1,1,1,1, np.log(1/s0w**2), np.log(1/s0t**2)))
  # function that evaluates the log of the target distribution at given parameter values
  tar = lambda at: tar_at(at, datay, datax, m0w, s0w, m0t, s0t)
  # function that evaluates the negative log of the target distribution to evaluate MAP estimates
  mapp = lambda at: -tar(at)

  res = minimize(mapp, at0)
  pars = res.x
  V = res.hess_inv
  L = np.linalg.cholesky(V)


  # Function that draws sample from a Gaussian random walk jumping distribution
  jump = lambda A: jumprwg(A, L)


  rr = np.random.normal(0,1,size=(6,Nc))

  A0 = np.matlib.repmat(pars.T,Nc,1).T + np.matmul(L,rr)


  sam = mcmcmh(Mc,Nc,M0,Q,A0,tar,jump)
  return 1/np.sqrt(np.exp(sam[0][0,-2:]))

# Decaying exponential
def DecayExpFunction(a, b, f, x):
    '''
    decaying exponential function evaluated at x with parameters a, b and f
    '''
    return a * np.exp(-b * x) * np.sin(2 * np.pi * f * x)


# Decaying exponential - first derivative
def DecayExpFunction1der(a, b, f, x):
    '''
    first derviative of the decaying exponential function evaluated at x with parameters a, b and f
    '''
    return a * np.exp(-b * x) * ((2 * np.pi * f) * np.cos(2 * np.pi * f * x) - b * np.sin(2 * np.pi * f * x))


# Decaying exponential - second derivative
def DecayExpFunction2der(a, b, f, x):
    '''
    second derviative of the decaying exponential function evaluated at x with parameters a, b and f
    '''
    return a * np.exp(-b * x) * ((-np.power((2 * np.pi * f), 2)) * np.sin(2 * np.pi * f * x)
                                 - ((4 * b * np.pi * f) * np.cos(2 * np.pi * f * x)) + b * np.sin(2 * np.pi * f * x))


class MCMCMH_NJ():
    '''
    Bayesian Noise and jitter reduction algorithm. MCMC used to determine the noise and jitter variances.
    Noise and jitter variances are then used in an iterative algorithm to remove the noise and jitter from the signal
    '''

    def __init__(self, fs, ydata, N, niter, tol, m0w, s0w, m0t, s0t, Mc, M0, Nc, Q):
        'Setting initial variables'

        # variables for AnalyseSignalN and NJAlgorithm
        self.fs = fs
        self.ydata = ydata
        # self.xdata = xdata
        self.N = N
        self.niter = niter
        self.tol = tol
        self.m0w = m0w
        self.s0w = s0w
        self.m0t = m0t
        self.s0t = s0t
        self.Mc = Mc
        self.M0 = M0
        self.Nc = Nc
        self.Q = Q
        # outs = MCMCMH.mcmcm_decayexp.main(ydata, xdata, m0w, s0w, m0t, s0t, Mc, M0, Nc, Q)
        # self.jitterSD = outs[0]
        # self.noiseSD = outs[1]

    def AnalyseSignalN(self):
        '''
        Analyse signal to remove noise and jitter providing signal estimates with associated
        uncertainty. Uses normalised independent variable
        '''

        # Initialisation
        self.N = np.int64(self.N)  # Converting window length integer to int64 format
        m = np.size(self.ydata)  # Signal data length
        m = np.int64(m)  # Converting signal length to int64 format

        # Setting initial variables
        n = (self.N - 1) // 2
        # Covariance matric for signal values
        Vmat = np.zeros((np.multiply(2, self.N) - 1, np.multiply(2, self.N) - 1))
        # Sensitivtity vecotrs
        cvec = np.zeros(n, self.N)
        # Sensitivtity matrix
        Cmat = np.zeros((self.N, np.multiply(2, self.N) - 1))
        # Initial signal estimate
        yhat0 = np.full((m, 1), np.nan)
        # Final signal estimate
        yhat = np.full((m, 1), np.nan)
        # Uncertainty infromation for estimates
        vyhat = np.full((m, self.N), np.nan)
        # Consistency matrix
        R = np.full((m, 1), np.nan)

        # Values of normalised independent variables
        datax = np.divide(np.arange(-n, n + 1), self.fs)

        outs =  mcmcm_main(self.ydata, datax, self.m0w, self.s0w, self.m0t, self.s0t, self.Mc,
                                                self.M0, self.Nc, self.Q)
        self.jitterSD = outs[0]
        self.noiseSD = outs[1]
        # Loop through indices L of window
        L = 0
        if np.size(self.ydata) > 10:
            # for L in range(1, m-self.N+1):
            # while
            # Index k of indices L of windows
            k = L + n
            # print(k)
            # Extract data in window
            datay = self.ydata[L:L + self.N]
            # Inital polynomial approximation
            p = np.polyfit(datax, datay, 3)
            pval = np.polyval(p, datax)
            yhat0[k] = pval[n]

            # Applying algortithm to remove noise and jitter
            [yhat[k], ck, vark, R[k]] = MCMCMH_NJ.NJAlgorithm(self, datax, datay, p, pval)
            print(yhat[k])
            # First n windows, start building the covariance matrix Vmat for the data
            if L < n + 1:
                Vmat[L - 1, L - 1] = vark

            # for windows n+1 to 2n, continue building the covariance matrix Vmat and start stroing the
            # sensitivtity vectors ck in cvec
            elif L > n and L < np.multiply(2, n) + 1:
                Vmat[L - 1, L - 1] = vark
                cvec[L - n - 1, :] = ck


            # For windows between 2n+1 and 4n, continue to build Vmat and cvec, and start building the sensitivtity
            # matrix Cmat from the sensitivtity vecotrs. Also, evaluate uncertainties for pervious estimates.
            elif L > np.multiply(2, n) and L < np.multiply(4, n) + 2:

                Vmat[L - 1, L - 1] = vark
                # Count for building sensitivtity matrix
                iC = L - np.multiply(2, n)
                # Start building sensitivtity matrix from cvec
                Cmat[iC - 1, :] = np.concatenate((np.zeros((1, iC - 1)), cvec[0, :], np.zeros((1, self.N - iC))),
                                                 axis=None)

                # Removing the first row of cvec and shift every row up one - creating
                # empty last row
                cvec = np.roll(cvec, -1, axis=0)
                cvec[-1, :] = 0
                # Update empty last row
                cvec[n - 1, :] = ck
                Cmatk = Cmat[0:iC, 1:self.N - 1 + iC]

                # Continue building Vmat
                Vmatk = Vmat[1:self.N - 1 + iC, 1:self.N - 1 + iC]
                V = np.matmul(np.matmul(Cmatk, Vmatk), np.transpose(Cmatk))
                vhempty = np.empty((1, self.N - iC))
                vhempty[:] = np.nan
                # Begin building vyhat
                vyhat[L, :] = np.concatenate((vhempty, V[iC - 1, :]), axis=None)


            # For the remaining windows, update Vmat, Cmat and cvec. Continue to
            # evaluate the uncertainties for previous estimates.
            elif L > np.multiply(4, n) + 1:
                # Update Vmat
                Vmat = np.delete(Vmat, 0, axis=0)
                Vmat = np.delete(Vmat, 0, axis=1)
                Vmatzeros = np.zeros([Vmat.shape[0] + 1, Vmat.shape[1] + 1])
                Vmatzeros[:Vmat.shape[0], :Vmat.shape[1]] = Vmat
                Vmat = Vmatzeros
                Vmat[2 * self.N - 2, 2 * self.N - 2] = vark

                # Building updated Cmat matrix
                Cmat_old = np.concatenate((Cmat[1:self.N, 1:2 * self.N - 1], np.zeros([self.N - 1, 1])), axis=1)
                Cmat_new = np.concatenate((np.zeros([1, self.N - 1]), cvec[0, :]), axis=None)
                Cmat = np.concatenate((Cmat_old, Cmat_new[:, None].T), axis=0)

                # Update cvec
                cvec = np.roll(cvec, -1, axis=0)
                cvec[-1, :] = 0

                # Continue building vyhat
                V = np.matmul(np.matmul(Cmat, Vmat), np.transpose(Cmat))
                vyhat[L, :] = V[self.N - 2, :]

        L += 1

        return (yhat[k])

    def NJAlgorithm(self, datax, datay, p0, p0x):
        '''
        Noise and Jitter Removal Algorithm- Iterative scheme that preprocesses data to reduce the effects of
        noise and jitter, resulting in an estimate of the true signal along with its associated uncertainty.

        Refer paper for details: https://ieeexplore.ieee.org/document/9138266
        '''

        # Initialisatio
        iter_ = 0
        delta = np.multiply(2, self.tol)

        # Values of basis function at central point in window
        N = np.size(datax)
        n = np.divide(self.N - 2, 2)
        k = np.int64(n + 1)
        t = np.array([np.power(datax[k], 3), np.power(datax[k], 2), datax[k], 1])
        # Deisgn Matrix
        X = np.array([np.power(datax, 3) + 3 * np.multiply(np.power(self.jitterSD, 2), datax),
                      np.power(datax, 2) + np.power(self.jitterSD, 2), datax, np.ones(np.size(datax))])
        X = X.T

        # Iterative algortithm
        while delta >= self.tol:
            # Increment number of iterations
            iter_ = iter_ + 1

            # Step 2 - Polynomial fitting over window
            pd = np.polyder(p0)
            pdx = np.polyval(pd, datax)

            # Step 4
            # Weight calculation
            w = np.divide(1, [np.sqrt(np.power(self.jitterSD, 2) * np.power(pdx, 2)
                                      + np.power(self.noiseSD, 2))])
            w = w.T

            # Calculating polynomial coeffs
            Xt = np.matmul(np.diagflat(w), X)
            C = np.matmul(np.linalg.pinv(Xt), np.diagflat(w))
            datay = datay.T
            p1 = np.matmul(C, datay)
            p1x = np.polyval(p1, datax)

            # Step 5 - stablise process
            delta = np.max(np.abs(p1x - p0x))
            p0 = p1
            p0x = p1x

            if iter_ == self.niter:
                print('Maximum number of iterations reached')
                break

        # Evaluate outputs
        c = np.matmul(t, C)
        yhat = np.matmul(c, datay)
        pd = np.polyder(p0)
        pdx = np.polyval(pd, datax[k])
        vk = np.power(self.jitterSD, 2) * np.power(pdx, 2) + np.power(self.noiseSD, 2)
        R = np.power(np.linalg.norm(np.matmul(np.diagflat(w), (datay - np.matmul(X, p0)))), 2)

        return yhat, c, vk, R


def random_gaussian_whrand(M, mu, sigma, istate1, istate2):
    '''
    Generates random numbers from a Gaussian Distribution using the Wichmann–Hill random number generator

    Inputs:
    M:        Number of random numbers required
    mu:       Mean of the Gaussian
    sigma:    Std of the Gaussian
    istate1:  vector of 4 integers
    istate2:  vector of 4 different integers

    Output:
    xdist:    Random Gaussian vector of size M
    '''
    mn = 0
    ndist = np.zeros(M)
    while mn < M:
        rr1 = whrand(istate1, 1)
        rr2 = whrand(istate2, 1)

        v1, istate1 = rr1
        v2, istate2 = rr2

        if mn < M:
            ndist[mn] = math.sqrt(-2 * math.log(v1)) * math.cos(2 * math.pi * v2)
            mn = mn + 1

        if mn < M:
            ndist[mn] = math.sqrt(-2 * math.log(v1)) * math.sin(2 * math.pi * v2)
            mn = mn + 1

        xdist = mu + sigma * ndist

    return xdist, istate1, istate2


def whrand(istate, N):
    '''
    Generates uniform random numbers between 0 and 1 using the Wichmann–Hill random number generator

    Inputs:
    istate:  vector of 4 integers
    N:       Number of random numbers required

    Outputs:
    r:       Vector uniform random numbers of size M
    istate:  Output vector of 4 integers
    '''

    # Constants
    a = np.array([11600, 47003, 23000, 33000])
    b = np.array([185127, 45688, 93368, 65075])
    c = np.array([10379, 10479, 19423, 8123])
    d = np.array([456, 420, 300, 0]) + 2147483123

    r = np.zeros(N)
    for i in range(N):
        # Update states
        for j in range(4):
            istate[j] = a[j] * np.mod(istate[j], b[j]) - c[j] * np.fix(istate[j] / b[j])
            if istate[j] < 0:
                istate[j] = istate[j] + d[j]

        # Evaluate random number
        w = np.sum(np.divide(istate, d))
        r[i] = np.remainder(w, 1)

    return r, istate

def njr(fs, ydata, N, niter, tol, m0w, s0w, m0t, s0t, Mc, M0, Nc, Q):
    analyse_fun = MCMCMH_NJ(fs, ydata, N, niter, tol, m0w, s0w, m0t, s0t, Mc, M0, Nc, Q)
    yhat1= analyse_fun.AnalyseSignalN()
    return yhat1


########################################
class NJRemoved(AgentMET4FOF):
    def init_parameters(self, fs=100, ydata = np.array([]),  N=15, niter=100, tol=1e-9, m0w = 10, s0w = 0.0005, m0t = 10, s0t = 0.0002*100/8, Mc=5000, M0=100, Nc=100, Q=50 ):
        self.fs = fs
        self.ydata = ydata
        self.N = N
        self.niter = niter
        self.tol = tol
        self.m0w = m0w
        self.s0w = s0w
        self.m0t = m0t
        self.s0t = s0t
        self.Mc = Mc
        self.M0 = M0
        self.Nc = Nc
        self.Q = Q


    def on_received_message(self, message):
        ddata = message['data']
        self.ydata = np.append(self.ydata, ddata)
        if np.size(self.ydata) == self.N:
            t = njr(self.fs, self.ydata, self.N, self.niter, self.tol, self.m0w, self.s0w, self.m0t, self.s0t, self.Mc, self.M0,self.Nc, self.Q)
            self.send_output(self.ydata[7] - t)
            self.ydata = self.ydata[1:self.N]
