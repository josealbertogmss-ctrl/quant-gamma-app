import numpy as np
from scipy.stats import norm

def calc_gamma_vectorized(
    S,
    K,
    sigma,
    T,
    r=0.0
):

    sigma = np.maximum(
        sigma,
        0.0001
    )

    T = np.maximum(
        T,
        1/365
    )

    d1 = (
        np.log(S / K)
        + (r + 0.5 * sigma**2) * T
    ) / (
        sigma * np.sqrt(T)
    )

    gamma = (
        norm.pdf(d1)
        / (
            S
            * sigma
            * np.sqrt(T)
        )
    )

    return gamma
