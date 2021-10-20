import numpy as np


# The famous Willingale et. al 2007 model
@np.vectorize
def w07(x, T, F, alpha, t):
    before = lambda x: np.log10(
        np.power(10, F) * np.exp(alpha - alpha * (np.power(10, x) / np.power(10, T))) * np.exp(-t / np.power(10, x))
    )
    after = lambda x: np.log10(
        np.power(10, F) * np.power((np.power(10, x) / np.power(10, T)), (-alpha)) * np.exp(-t / np.power(10, x))
    )
    vals = np.piecewise(x, [np.power(10, x) < np.power(10, T), np.power(10, x) >= np.power(10, T)], [before, after])
    return vals


def sharp_bpl(x, T, F, alpha1, alpha2):

    linT, linF = np.power(10, [T, F])
    linX = np.power(10, x)

    before = lambda x: linF * (x / linT) ** (-alpha1)
    after = lambda x: linF * (x / linT) ** (-alpha2)
    vals = np.piecewise(linX, [linX < linT, linX >= linT], [before, after])

    return np.log10(vals)


@np.vectorize
def smooth_bpl(x, T, F, alpha1, alpha2, S):

    linT, linF, linX = np.power(10, [T, F, x])
    return np.log10(linF * ((x / linT) ** (alpha1 * S) + (linX / linT) ** (alpha2 * S)) ** (-1 / S))


def chisq(x, y, yerr, model, *p):
    """
    Calculate chisq for a given proposed solution

    chisq = Sum_i (Y_i - model(X_i, F, T, alpha, t))^2 / Y_err_i^2,

    """

    x = np.asarray(x)
    y = np.asarray(y)
    yerr = np.asarray(yerr)
    if any(yerr == 0):
        print("Y_err of 0 provided. This is not gonna end well...")

    return np.sum(np.square(y - model(x, *p)) / np.power(yerr, 2))


def probability(reduced_chisq, nu, tt=0):
    import scipy.integrate as si
    from scipy.special import gamma

    integrand = lambda x: (2 ** (-nu / 2) / gamma(nu / 2)) * np.exp(-x / 2) * x ** (-1 + nu / 2)

    y, yerr = si.quad(integrand, reduced_chisq * nu, np.inf)

    return y
