import numpy as np

# Physical constants
G = 6.67430e-11
MPC_TO_M = 3.085677581e22
MSUN_TO_KG = 1.98847e30


def E_z(z, Omega_m, Omega_L=None):
    """
    Dimensionless Hubble parameter E(z)
    Assumes flat cosmology if Omega_L not provided.
    """
    if Omega_L is None:
        Omega_L = 1.0 - Omega_m

    return np.sqrt(Omega_m * (1 + z)**3 + Omega_L)


def critical_density_z(z, H0, Omega_m, Omega_L=None):
    """
    Critical density at redshift z in kg/m^3

    H0 in km/s/Mpc
    """
    # Convert H0 to s^-1
    H0_si = (H0 * 1000) / MPC_TO_M

    Hz = H0_si * E_z(z, Omega_m, Omega_L)

    rho_c = 3 * Hz**2 / (8 * np.pi * G)

    return rho_c


def overdensity_radius(M_delta,
                       z,
                       H0=70.0,
                       Omega_m=0.3,
                       Omega_L=None,
                       Delta=500):
    """
    Compute R_Delta in Mpc

    Parameters
    ----------
    M_delta : float
        Mass in solar masses
    z : float
        Redshift
    H0 : float
        Hubble constant (km/s/Mpc)
    Omega_m : float
        Matter density parameter
    Omega_L : float
        Dark energy density parameter (optional, flat if None)
    Delta : float
        Overdensity definition (e.g. 200, 500)

    Returns
    -------
    R_delta_Mpc : float
        Radius in Mpc
    """

    rho_c = critical_density_z(z, H0, Omega_m, Omega_L)

    # Convert mass to kg
    M_kg = M_delta * MSUN_TO_KG

    # Radius in meters
    R_m = ((3 * M_kg) / (4 * np.pi * Delta * rho_c))**(1/3)

    # Convert to Mpc
    R_Mpc = R_m / MPC_TO_M

    return R_Mpc

def rxcj1115():
    mass = 6.86e14  # Msun
    z = 0.350
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.27)
    print(f'RXCJ1115+0129: R500 = {r:1.2f} Mpc')

def twoA0335():
    mass = 2.27e14  # Msun
    z = 0.036
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'2A0355+096: R500 = {r:1.2f} Mpc')

def a478():
    mass = 6.95e14  # Msun
    z = 0.088
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'A479: R500 = {r:1.2f} Mpc')

def rxj1720():
    mass = 6.95e14  # Msun
    z = 0.164
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'RXJ1720+2368: R500 = {r:1.2f} Mpc')

def rxj2129():
    mass = 4.33e14  # Msun
    z = 0.234
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'RXJ2129+0005: R500 = {r:1.2f} Mpc')

def a2206():
    mass = 1.84e14  # Msun
    z = 0.152
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'A2206: R500 = {r:1.2f} Mpc')

def ms1455():
    mass = 3.5e14  # Msun
    z = 0.152
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'MS1455+2232: R500 = {r:1.2f} Mpc')

def a1413():
    mass = 5.95e14  # Msun
    z = 0.152
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'A1413: R500 = {r:1.2f} Mpc')

def actj0022():
    mass = 5.5e14  # Msun
    z = 0.81
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'ACTJ0022-0036: R500 = {r:1.2f} Mpc')

def z3146():
    mass = 6.53e14  # Msun
    z = 0.289
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'Z3146: R500 = {r:1.2f} Mpc')

def a1795():
    mass = 4.57e14  # Msun
    z = 0.062
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'A1795: R500 = {r:1.2f} Mpc')

def a2626():
    mass = 1.84e14  # Msun
    z = 0.062
    r = overdensity_radius(mass, z, H0=70, Omega_m=0.3)
    print(f'A2626: R500 = {r:1.2f} Mpc')

twoA0335()
rxcj1115()
rxj1720()
a478()
rxj2129()
a2206()
ms1455()
a1413()
actj0022()
z3146()
a1795()
a2626()