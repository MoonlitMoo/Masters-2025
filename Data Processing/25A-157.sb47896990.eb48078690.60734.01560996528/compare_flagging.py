import re

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import tight_layout

with open("Data Processing/25A-157.sb47896990.eb48078690.60734.01560996528/full_result.txt") as f:
    f_results = np.array([float(line.split(":")[-1].split("%")[0]) for line in f.readlines() if re.match(r"\d+: \d+.\d+%", line)])
with open("Data Processing/25A-157.sb47896990.eb48078690.60734.01560996528/parallel_result.txt") as f:
    p_results = np.array([float(line.split(":")[-1].split("%")[0]) for line in f.readlines() if re.match(r"\d+: \d+.\d+%", line)])
print(f_results)
print(p_results)
x = np.arange(len(f_results))
width = 0.35

# Create the plot
fig, ax = plt.subplots()
bars2 = ax.bar(x - width/2, p_results, width, label='Parallel')
bars1 = ax.bar(x + width/2, f_results, width, label='Full')
plt.xlabel("SPW")
plt.ylabel("Flagging [%]")
plt.grid()
ax.legend()
plt.title("Flagging percent with and without crosshands")
plt.savefig("compare.png", dpi=300)

plt.figure()
plt.bar(x, (f_results / p_results - 1) * 100)
plt.xlabel("SPW")
plt.ylabel("Change in flagging [%]")
plt.grid()
plt.title("Change in flagging amount when cross hands included")
plt.savefig("change.png", dpi=300)
