import numpy as np

from astropy.cosmology import FlatLambdaCDM
import astropy.units as u
import astropy.cosmology.units as cu

def calc_power(z, alpha, sigma_alpha, S, sigma_S):
    cosmo = FlatLambdaCDM(H0=70.0, Om0=0.3)
    d_L = cosmo.luminosity_distance(z)

    P = (4 * np.pi * d_L ** 2) / (1 + z) ** (1 - alpha) * (1.4 / 10) ** (-alpha) * S / 1000 * u.Jy
    sigma_P = np.sqrt(((sigma_S / S) ** 2 + (np.log(1 + z) - np.log(1.4 / 10)) ** 2 * sigma_alpha) * P ** 2)
    return P.to(u.W / u.Hz) / 1e24, sigma_P.to(u.W / u.Hz) / 1e24

a478 = (0.088, 0.88, 0.03, 5.41, 0.03)
rxj1720 = (0.161, 0.85, 0.03, 1.27, 0.07)
rxcj1115 = (0.34, 0.67, 0.07, 2.27, 0.21)
rxj2129 = (0.234, 0.78, 0.02, 5.36, 0.18)

r1 = calc_power(*rxj1720)
r2 = calc_power(*a478)
r3 = calc_power(*rxcj1115)
r4 = calc_power(*rxj2129)

print(f"RXJ1720: {r1[0].value:.3f} +/- {r1[1].value:.3f} 10^24 W/Hz")
print(f"A478: {r2[0].value:.3f} +/- {r2[1].value:.3f} 10^24 W/Hz")
print(f"RXCJ1115: {r3[0].value:.3f} +/- {r3[1].value:.3f} 10^24 W/Hz")
print(f"RXJ2129: {r4[0].value:.3f} +/- {r4[1].value:.3f} 10^24 W/Hz")

