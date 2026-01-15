# Plotting the synchrotron aging using sychrofit python package
import numpy as np
import matplotlib.pyplot as plt
from sf import synchrofit

# Plotting consts
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12

# Model parameters
frequencies = np.logspace(np.log10(100e6), np.log10(2e10), 1000)  # 100 MHz to 20 GHz
alpha_inject = 0.6
s_inject = 2 * alpha_inject + 1 # Injection energy distribution
ds_inject = 0.  # Uncertainity in s
break_freq = np.log10(5e9)  # 1 GHZ
dbreak_freq = 0.
remnant_predict = 0.  # Fractional inactive time?
dremnant_predict = 0.
norm = 1.

fig, ax = plt.subplots(1, 1)
inj = np.power(frequencies, -alpha_inject)

# Normalise all to JP 
models = ["JP", "KP", "CI"]
jp_0 = 0
for m in models:
    results = synchrofit.spectral_model_(
        params=(m,
        break_freq, dbreak_freq,
        s_inject, ds_inject,
        remnant_predict, dremnant_predict,
        norm
        ),
        frequency=frequencies
    )

    model_data = results[0]
    if m == "JP":
        jp_0 = model_data[0]
        ax.plot(frequencies, inj * jp_0/inj[0], label="Injection", c='k')
    if m != "JP":
        model_data *= jp_0 / model_data[0]
    ax.plot(frequencies, model_data, label=m)

ax.set_yscale('log')
ax.set_xscale('log')
ax.set_ylabel("Flux density [arbitrary units]")
ax.set_xlabel("Frequency [arbitrary units]")
ax.grid()
ax.legend()
plt.savefig("synchro_aging.pdf", dpi=300)