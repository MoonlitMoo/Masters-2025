# rflag testing (1)

Initial attempt

```python
uvsub(vis=msname)
# Clean minimal RFI spw 16~25
flagdata(vis=msname, mode='rflag', field='0', spw='16~25', datacolumn='corrected', 
	action='apply', flagbackup=False)
# Extra filtering over 26, 27
flagdata(vis=msname, mode='rflag', field='0', spw='26~27', extendpols=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# Clean next region
flagdata(vis=msname, mode='rflag', field='0', spw='28~36', extendpols=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# Deal with the remaining (bar 45)
flagdata(vis=msname, mode='rflag', field='0', spw='37~44,46,47', extendpols=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='rflag', field='0', spw='45', extendpols=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
uvsub(vis=msname, reverse=True)
```

![image.png](rflag%20testing%20(1)/image.png)

I don’t like this since it removes way too much data.~30-45% → 70~90% and 87% → 99%.