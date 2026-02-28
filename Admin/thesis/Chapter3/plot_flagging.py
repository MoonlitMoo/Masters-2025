import numpy as np
import matplotlib.pyplot as plt

f_scale = 1.0
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale

# Load data
pre = np.load("unflagged_data.npy")
post = np.load("aoflagger_data.npy")

# Extract x (frequency) and y (amplitude)
freq_pre, amp_pre = pre[:, ::20]
freq_post, amp_post = post[:, ::20]

print(amp_pre.shape)
print(amp_post.shape)

# Create 1x2 subfigure
fig, axes = plt.subplots(1, 2, figsize=(8, 4))

# Pre-flag
axes[0].plot(freq_pre, amp_pre, ',', alpha=0.5)
axes[0].set_title("Pre-flagging")
axes[0].set_ylabel("Amplitude")

# Post-flag
axes[1].plot(freq_post, amp_post, ',', alpha=0.5)
axes[1].set_title("Post-flagging")
fig.supxlabel("Frequency (GHz)")

# RFI regions
rfi = [(9.3, 9.5), (10.7, 12)]
for ax in axes:
    for r in rfi:
        f0, f1 = r
        ax.axvspan(f0, f1, alpha=0.1, color="grey")
        ax.axvspan(f0, f1, alpha=0.1, color="grey")
for ax in axes:
    ax.grid(alpha=0.5)

# Clipping
axes[0].set_ylim(0, 0.2)
axes[1].set_ylim(0, 0.08)

plt.tight_layout()
plt.savefig("flagging_comparison.pdf", dpi=300)