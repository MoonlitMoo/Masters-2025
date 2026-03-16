# Flagging notes

# Broadband intermittent RFI

![image.png](Flagging%20notes/image.png)

- Wide bandwidth, but not constant in time.
- Can see spikes in time, wide peaks in frequency.

## TFcrop

```python
flagdata(vis=msname, mode='tfcrop', field='0', spw='10~11', 
	maxnpieces=4, timecutoff=2.5, freqcutoff=3.0, timefit='poly', extendflags=False, 
	action='calculate', display='both')
```

Smaller time cutoff, freq cutoff. Time poly fit and less pieces. Removed extend flags. 

Then follow up with an extend command flagging near time and freq. 

# Narrow spiky RFI

- narrow bandwidth, extended in time.
- Can see noise in time, spikes in freq

## Manual

```python
flagdata(vis=msname, mode='manual', field='0', spw='16:0')
```

Straight up kill the channel. 

## TFcrop

# Checkerboard RFI

## TFcrop

```python
cmdlist = ["mode='tfcrop' field='0137+331=3C48' spw='21,22' maxnpieces=5 timecutoff=2.5 freqcutoff=2.5 usewindowstats='sum' extendflags=False",
"mode='extend' field='0137+331=3C48' spw='21,22' scan='23' growtime=75.0 extendpols=True",
"mode='extend' field='0137+331=3C48' spw='21,22' scan='24' growtime=50.0 extendpols=True"]
```

Can drop cutoff values and maxnpieces. Use window stats sum. Grow time and extend across pols. 

# AOflagger

[https://aoflagger.readthedocs.io/en/latest/](https://aoflagger.readthedocs.io/en/latest/)

1. https://arxiv.org/pdf/1002.1957 ✅
2. [https://arxiv.org/pdf/1201.3364](https://arxiv.org/pdf/1201.3364)
3. [https://arxiv.org/pdf/2301.01562](https://arxiv.org/pdf/2301.01562)

## Thresholding

- Surface fitting. Make a polynomial lstq fit over the data, removing points outside threshold of fit. Iterate the process, only considering unflagged data.
- Smoothing. Sliding window using the median (less susceptible to deviations due to peaks). Can improve by weighting via a Gaussian function.
- Cumulative sum, exceeds threshold then start flagging until it fixes. Threshold is adaptive and calculated based on distribution parameters.
- VarThreshold. Instead of individual thresholding, can see if all sequential/neighbouring pixels are above a smaller threshold. Use decreasing thresholds for larger pixel groups → Starts to consider morphology if you get initial candidates from individual and only consider VarThreshold for neighbouring candidates.
    - Said threshold is set as a multiple of the mode of individual pixels and as a function of the number of considered pixels.
- SumThreshold. Basically the same as the above, but looks at the total of the selected pixels compared to a threshold. Thresholds are then applied differently, work low → highest, replacing flagged values with threshold value. Stop extra flagging if only few points are really high, since cumsum would flag normal value points.
- Single value decomposition. Compute the SVD of the baseline-freq vs time matrix $A = U \Sigma V^T$ ($U$ is $m\times m$ orthogonal matrix, V is the orthogonal $n\times n$ matrix, $\Sigma$ is the $m\times n$ diagonal matrix, with decreasing values.). Then curve fit the singular values and we assume RFI is a discontinuity at the start of the curve somewhere. Replace all those values with 0, then calculate $A^*$, boom RFI removed. Not perfect as all RFI only removed if columns are independent, blah blah. Faint RFI may be left in curve fit, etc.

## Scale invariant rank operator

- Statistical function that operates on flags only. Considers a sample to be flagged if a percentage of the sequence are already flagged.
- Operates in each direction independently, order changes things a little. The aggressiveness can be controlled via the parameter $\eta$ which defines required percentage within the subsequence.

## Notes

- Doesn’t matter if data is calibrated or uncalibrated. Doesn’t matter what type of polarisation/correlation you are looking at.
- For best results, the length and width of the window should be about three
times the Gaussian kernel size or larger.

# Things to try

- Extend polarisations
- Adjust the gaussian kernel size to match VLA data.
- Run aoflagger on flagged data with keepflags as true
- Try making self calibration with longer solve interval