# Phase flagging (1)

The flagging is on the bandpass, not the actual thingy. Need to see if I can transfer back somehow.

- Flag whole antenna, or sub parts
- Criteria to flag an antenna (per SPW)

```python
 plotms(vis=f'{name}.G0all',xaxis='time',yaxis='phase', coloraxis='corr',iteraxis='antenna', spw='45')
```