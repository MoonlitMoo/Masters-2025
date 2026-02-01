# Open the file
files = ["c_observations.csv", "d_observations.csv"]
configs = ["C", "D"]

results = {}
for file, config in zip(files, configs):
	with open(file, "r") as f:
		for line in f.readlines():
			if "secs" not in line:  # Blank line / header
				continue
			source, time_str, ra, dec, date = line.split(",")
			if source.startswith("J") or "3C" in source:  # Calibrator
				continue
			time = int(time_str.split(' ')[0])
			source = source.strip()
			if source in results:
				results[source].append([config, date.strip(), time/60])
			else:
				results[source] = [[config, date.strip(), time/60]]

for k, v in results.items():
	print(k)
	for obs in v:
		print(f"\t{obs[0]}\t{obs[1]}\t{obs[2]:.1f}")
