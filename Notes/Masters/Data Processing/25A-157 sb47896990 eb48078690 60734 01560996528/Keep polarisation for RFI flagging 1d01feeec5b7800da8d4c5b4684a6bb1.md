# Keep polarisation for RFI flagging?

Did initial trimming without cross-hands.

Ran same flagging commands but including the crosshands. Made sure that extend included the polarisations. Code below. 

```python
# 10~11 
cmdlist = ["mode='tfcrop' field='0137+331=3C48' spw='10~11' maxnpieces=4 timecutoff=2.5 freqcutoff=2.5 timefit='poly' extendflags=False", 
	"mode='extend' field='0137+331=3C48' scan='23' spw='10~11' growtime=75.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True",
	"mode='extend' field='0137+331=3C48' scan='24' spw='10~11' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 16
flagdata(vis=msname, mode='manual', field='0137+331=3C48', spw='16:0~2')
# 21, 22
cmdlist = ["mode='tfcrop' field='0137+331=3C48' spw='21,22' maxnpieces=5 timecutoff=2.5 freqcutoff=2.5 usewindowstats='sum' extendflags=False", 
	"mode='extend' field='0137+331=3C48' spw='21,22' scan='23' growtime=75.0 extendpols=True",
	"mode='extend' field='0137+331=3C48' spw='21,22' scan='24' growtime=50.0 extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 25~28 and 30,31 (30, 31 still have some time spikes)
cmdlist = ["mode='tfcrop' field='0137+331=3C48' spw='25~28,30~31' maxnpieces=4 timecutoff=2.5 freqcutoff=2.5 timefit='poly' extendflags=False",
  "mode='extend' field='0137+331=3C48' scan='23' spw='25~28,30~31' growtime=75.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True",
  "mode='extend' field='0137+331=3C48' scan='24' spw='25~28,30~31' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 29, not perfect but works for now
cmdlist = ["mode='manual' field='0137+331=3C48' spw='29:2;9;10;19;40'",
	"mode='tfcrop' field='0137+331=3C48' spw='29' maxnpieces=3 timecutoff=2.5 freqcutoff=2.5 timefit='poly' extendflags=False",
  "mode='extend' field='0137+331=3C48' scan='23' spw='29' growtime=75.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True",
  "mode='extend' field='0137+331=3C48' scan='24' spw='29' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
```

Ran this on **parallel** and **full** datasets. 

```python
flagInfo = flagdata(vis=msname, mode='summary', field='2')
for hand in ["LL", "RR", "LR", "RL"]:
	if hand not in flagInfo['correlation'].keys():
		continue
	print(f"{hand}: {flagInfo['correlation'][hand]['flagged'] / flagInfo['correlation'][hand]['total'] * 100 :.2f}%")
for spw in range(0, 32):
	print(f"{spw}: {flagInfo['spw'][str(spw)]['flagged'] / flagInfo['spw'][str(spw)]['total'] * 100:.2f}%")
```

# Parallel results

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image.png)

# Full results

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image%201.png)

# Comparison

- Little visible by eye on above graphs
- In total LL/RR flagged 33.81% → 36.44% increase of 8%
- Looking at individual spectral windows
    
    ![compare.png](Keep%20polarisation%20for%20RFI%20flagging/compare.png)
    
    ![change.png](Keep%20polarisation%20for%20RFI%20flagging/change.png)
    

## Compare SPW 10, 11

Full data

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image%202.png)

Parallel data

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image%203.png)

## Compare SPW 21, 22

Full data

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image%204.png)

Parallel data

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image%205.png)

## Compare SPW 25~28

Full data

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image%206.png)

Parallel data

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image%207.png)

## Compare SPW 29~31

Full data

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image%208.png)

Parallel data

![image.png](Keep%20polarisation%20for%20RFI%20flagging/image%209.png)

# Conclusion

- Looks like keeping the cross-hands in identical runs flags a decent bit more data.
- It doesn’t make everything a ton better (esp in complicated), but there seems to be an amount of improvement.
- No tuning was done, so perhaps could improve more but time vs reward in the pre-calibration phase.
- SPW 10 seemed to have a notch into it where I didn’t expect ~9.35 GHz, could be a mistake, but I’ll leave it.