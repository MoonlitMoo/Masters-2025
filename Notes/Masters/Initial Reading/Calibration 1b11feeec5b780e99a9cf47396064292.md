# Calibration

# The measurement equation

The fields of an incoming electric field can be described by a 2D vector in the perpendicular plane. Effects that modify the electric field can then be represented as a sequence of $2\times2$ matrices.

$$
\bar e' = \mathbf J_N \dots \mathbf J_2 \mathbf J_1 \bar e
$$

The electric fields create a voltage on the antenna, which we can model as another Jones matrix applied to the electric field so that $\bar v = \mathbf J \bar e$. Since interferometers correlate between two signals (from antenna $p, q$) averaged over a time period, this can also be written as

$$
\mathbf V_{pq} = \mathbf J_p \mathbf B \mathbf J_q^H
$$

Where $\mathbf V_{pq}$ is the complex visibility that we get from the antenna, and $\mathbf B$ is the brightness of the sky. This is the most basic form of the measurement equation.

## Adding u,v,w offset

We also have to account for phase offsets due to the antenna position in $(u,v,w)$ space. This can be found as another Jones matrix $\mathbf K$.

$$
\mathbf K_i = e^{-2\pi i (u_il + v_im + w_i(n-1))}
$$

Which we can insert into the measurement equation like so

$$
\mathbf V_{pq} = \mathbf J_p \mathbf K_p \mathbf B \mathbf K_q^H\mathbf J_q^H = \mathbf J_p \mathbf X_{pq} \mathbf J_q^H
$$

Where $\mathbf X_{pq}$ is the source coherency. The full Jones chain has many components, which are listed left to right below.

1. $\mathbf K$, geometric delay
2. $\mathbf B$, bandpass
3. $\mathbf G$, electronic gains
4. $\mathbf D$, polarisation leakage
5. $\mathbf E$, antenna primary beam resp
6. $\mathbf X$, cross-hand phases
7. $\mathbf P$, parallactic angle 
8. $\mathbf T$, tropospheric effects
9. $\mathbf Z$, ionospheric effects

# Calibration

We measure $\mathbf V_{pq}$ and want to find $X_{pq}$ by fitting the instrumental parameters $J$. In general we can write this as $\min_J||\mathbf V - \mathbf{JBJ}^H||$. Because we have a ton of measurements, this is usually well constrained. Each antenna provides it’s own unknown that we need to solve for. Usually we only fit the geometric delay $\mathbf K$, the bandpass $\mathbf B$, and the gain $\mathbf G$. 

## Calibration sources

We can make use of calibrator sources, which are well defined objects in the sky. First tier sources allow for setting the absolute flux scale, bandpass, and polarisation. Second tier calibrators are for more time dependent effects like complex antenna gain, parallactic angle correction. Called transfer calibration.