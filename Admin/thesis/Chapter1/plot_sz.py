import numpy as np
import matplotlib.pyplot as plt

f_scale = 1.0
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale

# Constants (SI)
h = 6.62607015e-34
kB = 1.380649e-23
c = 299792458.0
Tcmb = 2.7255

# Prefactor
I0 = 2 * (kB * Tcmb)**3 / (h**2 * c**2)

def x_of_nu(nu_hz):
    return h * nu_hz / (kB * Tcmb)

def g_tsz(x):
    return x / np.tanh(x/2) - 4

def f_tsz(x):
    return (x**4 * np.exp(x) / (np.exp(x) - 1)**2) * g_tsz(x)

# Frequency range
nu_ghz = np.linspace(0.1, 800, 3000)
nu_hz = nu_ghz * 1e9
x = x_of_nu(nu_hz)

# Different y values to demonstrate scaling
y_values = [1e-5, 2e-5, 5e-5, 1e-4]

plt.figure()

for y in y_values:
    dI = I0 * y * f_tsz(x)
    # Convert to MJy/sr for nicer numbers
    dI_MJy = dI / 1e-20
    plt.plot(nu_ghz, dI_MJy, label=f"y = {y:.0e}")

plt.axvline(217, linestyle="--", c='k', linewidth=1)
plt.axhline(0, linestyle="-", c='k', linewidth=1)

plt.xlabel("Frequency (GHz)")
plt.ylabel(r"$\Delta I$ (MJy sr$^{-1}$)")

plt.grid()
plt.xlim(1, 800)
plt.legend()
plt.savefig("sz_ampl.pdf", dpi=300, bbox_inches='tight')
