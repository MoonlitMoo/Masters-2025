import numpy as np
from matplotlib import pyplot
from scipy.optimize import curve_fit

def fitfunc(x, *p):
    y=np.zeros_like(x)
    for i, pord in enumerate(p):
        y+=pord*x**i
    return y

def iterative_fit(x, y, p0, max_iter=3, sigma_thresh=3.0):
    # Fit the model, calculate deviation, then mask out those exceeding a threshold of said deviation and refit.
    mask = np.isfinite(y)
    for _ in range(max_iter):
        if np.sum(mask) < len(p0):  # Not enough points to fit
            return np.full_like(p0, np.nan)
        popt, pcov = curve_fit(fitfunc, x[mask], y[mask], p0=p0)
        residuals = y[mask] - fitfunc(x[mask], *popt)
        std = np.std(residuals)
        new_mask = np.abs(residuals) < sigma_thresh * std
        # Check if all within threshold, if so, done
        if np.all(new_mask):
            break
        # Update mask with new mask, if none are updated, done.
        tmp = mask.copy()
        mask[np.where(mask)[0][~new_mask]] = False
        if np.array_equal(tmp, mask):
            break
    return popt, pcov


visname='finalcalibrators.ms'
field=1 # not a string

# Get information from ms
msmd.open(visname)
nant=msmd.nantennas
nscan=len(msmd.scansforfield(field))
nspw=len(msmd.spwsforfield(field))
freqs=[]
for ispw in range(nspw):
    freqs.append(msmd.chanfreqs(ispw))
msmd.close()

# Open up bandpass table
bptable='testphase_inf_b_allspw.b'
tb.open(bptable)
flag=tb.getcol('FLAG')
snr=tb.getcol('SNR')
cpar=tb.getcol('CPARAM') # this is the gain solution
ant=tb.getcol('ANTENNA1')
spw=tb.getcol('SPECTRAL_WINDOW_ID')
scan=tb.getcol('SCAN_NUMBER')
snr[flag]=np.nan
cpar[flag]*=np.nan
tb.close()

# Copy the table to a new one which we will fill in with the fitted solutions
os.system('cp -r '+bptable+' bptable_fitted.b')
tb.open('bptable_fitted.b', nomodify=False)
cparnew = tb.getcol('CPARAM') # we will modify this and put it back in
flagnew=tb.getcol('FLAG')
flagnew[:,:,:] = False # false for not flagged, true for flagged

# cpar.shape is (npol, nchan, nscan*nant*nspw)
# Last column is ordered by spectral window, antenna, scan
# Fit a polynomial to phase across the whole bandwidth for each antenna, scan
nchan = len(freqs[0]) # ignoring pathological cases with different numbers of channels per spw...
allfreq = np.array(freqs).flatten()
nu0 = np.mean(allfreq)
for ea in np.unique(ant):
    for sc in np.unique(scan):
        inds = np.nonzero((ant==ea) & (scan==sc))[0] # should have length = nspw
        phase = np.zeros((2, nchan*nspw)) # 2 correlations
        amp = np.zeros_like(phase)
        sig = np.zeros_like(phase)
        for ispw in range(nspw):
            data = cpar[:,:,inds[ispw]]
            phase[:, ispw*nchan:(ispw+1)*nchan] = np.angle(data)*180/np.pi # deg
            amp[:, ispw*nchan:(ispw+1)*nchan] = np.abs(data)
            sig[:, ispw*nchan:(ispw+1)*nchan] = snr[:,:,inds[ispw]]
        # Fit the amp and phase for each correlation
        # To make a lot of figures...
        fig, ax=pyplot.subplots(2,1)
        polcols='km'
        fitpars = np.zeros((2,2,2))*np.nan
        for ipol in range(2):
            good = ~np.isnan(sig[ipol,:])
            if np.sum(good)==0: continue
            popt, pcov = iterative_fit(allfreq[good]/nu0, phase[ipol,good], p0=[0,0]) #, sigma=sig[ipol,good]) # fitting without sigma is better as just allows the greater number of good datapoints to overwhelm the bad ones.  Note you wouldn't want to do this if there was a chance of phasewrapping
            fitpars[ipol,0,:] = popt
            popt2, pcov2 = iterative_fit(allfreq[good]/nu0, amp[ipol,good], p0=[1,0])
            fitpars[ipol,1,:] = popt2
            ax[0].plot(allfreq[good]*1e-9, phase[ipol,good], ','+polcols[ipol])
            ax[0].plot(allfreq*1e-9, fitfunc(allfreq/nu0, *popt), polcols[ipol])
            ax[1].plot(allfreq[good]*1e-9, amp[ipol,good], ','+polcols[ipol])
            ax[1].plot(allfreq*1e-9, fitfunc(allfreq/nu0, *popt2), polcols[ipol])
            ax[0].set_xlabel('Freq / GHz')
            ax[1].set_xlabel('Freq / GHz')
            ax[0].set_ylabel('Phase / deg')
            ax[1].set_ylabel('Amp')
        fig.tight_layout()
        fig.savefig('plots/bpfit/ea%d_scan%d.png' % (ea+1,sc))
        pyplot.close('all')
        # Once you're sure the fits are good, put the points into the new table
        for ipol in range(2):
            if np.nansum(fitpars[ipol,0,:])==0:
                flagnew[ipol,:,inds] = True
                continue
            for ispw in range(nspw):
                phasefit = fitfunc(freqs[ispw]/nu0, *fitpars[ipol,0,:])*np.pi/180
                ampfit = fitfunc(freqs[ispw]/nu0, *fitpars[ipol,1,:])
                cparnew[ipol,:,inds[ispw]] = ampfit*np.exp(1j*phasefit)
            
tb.putcol('CPARAM', cparnew)
tb.putcol('FLAG', flagnew)
tb.flush()
tb.close()
