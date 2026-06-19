# Cluster papers

# Shortlist

https://arxiv.org/abs/2506.17526

Cluster finder strategies

## Context

- When we stare at a cluster, we get stuff in the foreground and the background. Therefore, multiple dark matter halos for the different groups. Leads to errors.
- Want to figure out systematic errors caused by optical cluster finders, especially regarding mass and richness.
- Similar to Cohn et al 2007 (**Red-sequence cluster finding in the Millennium Simulation)**.

## Method

- Use remapper algorithm on data from Cardinal. Only weird thing is that some galaxies associated with density peaks instead of resolved halos.
- Don’t consider subhalos, only isolated halos from ROCKSTAR (not GTA studio)
- Filter for halo masses > 6 10^12 h-1 M sun, which is good for z <0.5, above its a lower limit.
- Then bin them by richness, i.e. number galaxies with some probabilistic stuff.
- Flat LCDM cosmology.
- Use Fig 1 for explain

## Results

- Make a new way yo visualise contribution to cluster from halo (Fig2)
- z ~ .3 73% and 100% clean for lowest - highest richness. Where clean means ≥ 50% from main halo. For higher redshift (0.5), clean is ~20% for lowest richness bin.
- Calculate completeness of halos as a function of mass. This just means, what percentage of halos at a given mass where the main contributor to a cluster. For clusters of richness ≥20 this was 64% at 10^14h-1Msun
- Computed some metrics to find offset of redmapper cluster centre to the primary halo centre. Added some Xray noise since redmapper returns a galaxy as centre and all the halos have a galaxy at centre (i.e error could be 0). Found 70% are well centred, with mean offset of 40% cluster radius for miscentred ones.
- Framework only for redmapper, but framework compatible with whatever you want. Codes on github, go wild.

https://arxiv.org/abs/2507.11320

## Context

- Faint diffuse stuff is hard to detect, expecially when looking for cluster bridges and megahalos (out to R500).
- Got to do source subtractions and reimaging and all that is hard/not perfect/computationally expensive.
- We made a fish to try and skip the hard bit. TransUnet Network for radio Astronomy (TUNA)

## Method

- Based on TransUnet, which hot glues the Vision Transformer (image processing + contextual awareness) module and U-Net (localised feature extraction) together.
- TUNA uses ResNet-50 and 12 layer ViT encoder trained on ImageNet21k.
- Training data was syntehtic observation of diffuse structures from Enzo code with standard lamda cdm.
- They calculated synchrotron emission at 150 MHz from cosmic shocks. Ignored reacceleration here. Then stacked a bunch of redshift images with random rotations to get 500 light cones.
- Emulated 8hr observation of LOFAR for said images, add some noise and bang training/test data. Two sets of data, one at 6” and 20” beam size.

## Results

- Compared against R-Unet (Stuardi et al, 2024) **Radio U-Net: a convolutional neural network to detect diffuse radio sources in galaxy clusters and beyond**
Image 3
- Then they used LoTSS-DR2 (LOFAR Two-meter Sky Survey) data for real tests. Again 8hr observation with 6” resolution and 309 clusters in PSZ2. 
Image 5, Image 8
- It’s pretty good at processing raw images to get diffuse structure, skipping artefacts/noise/point sources. Seems better than previous similar algorithm. Has limitations of course.
- Took a ~3 minutes for 6” 9500x9500 pixel image to be processed on a HPC.

https://arxiv.org/abs/2508.10987

Most galaxies rotationally supported against gravity, a couple real big ones which are quiescent are dispersion supported called slow-rotators. None confirmed >2 by stellar kinematics, but here they think they found one at z=3.449 since morphology and spin matching that expected of slow rotator. Suggest merger activity could play a major role in formation/transformation of massive galaxies <2 Gyr which is earlier than expected.

https://arxiv.org/abs/2508.11819

## Context

- We were studying a dwarf galaxy that kinda looks like a tadpole and has an ultraluminous X-ray thing we wrote a different paper on.
- There was a bunch of diffuse X-ray stuff below it that wasn’t connected to the galactic disk which was weird, so we checked it out.
- Used HST, VLA, LOFAR data to double check features.

## Results

- Congrats its a new cluster at z = 0.5.
- From the X-ray there is asymmetrical morphology, core isn’t well defined, and higher than expected temperature, so it is likely quite young but not a proto-cluster.
- Radio lobe near a probable point source, which could be an AGN falling towards the centre.
- Image 3

https://arxiv.org/abs/2508.13053

## Context

- Filaments can form in the cosmic web where walls of matter intersect and collapse.
- Tidal torque theory predicts that asymmetry in this can cause torque such that filaments rotate when they form.

## Method

- Part of MIGHTEE survey of MeerKAT, using HI data. Resulting in 14 galaxies for the sample. Augmented with DESI + SDSS data + 283 galaxies in the range .03 - .034 z.
- Use Disperese program to determine the cosmic web and then compute distance of galaxies to filament.

## Results

- Original 14 galaxies part of a 1.7 Mpc by 36 kpc structure with a velocity dispersion of 140 km/s. Then that is within 1 Mpc of a filamentary structure from DESI and SDSS galaxies.
- Said large structure is 15.4 Mpc long and 0.8-1 Mpc wide. Image 2
- Plotting velocity of galaxy vs distance to filament shows that they look like they are rotating with it. Strongest example of this so far. Image 9
- Longest spinning structure found so far.

https://arxiv.org/abs/2508.13597

She spins and we could measure it

https://arxiv.org/abs/2505.05415

## Context

- Large radio halos with extents > 2 Mpc are becoming more and more common with better instruments.
- Cuciti et al 2022 suggests new class of mega-halos where diffuse extent out to R500 and often two component, first being classical halo, second being ultrasteep component in the outer regions (alpha ≥ -1.5).
- Investigate properties of radio halos of 5 clusters.
    - PLCK G287.0+32.9
    - Abell 2744
    - Bullet Cluster
    - MACS J0717+3745
    - Abell 2142
- New observations of the first three, published data for last two. New observations are in the range .55 GHz → 2.8 GHz by MeerKAT, varying per cluster. Some data from uGMRT 300-500 MHz.

## Results

- Radial radio progiles Figure 8
- Their results show the profiles can be fir with a single exponential, no need for second component. First high frequency measurement of radio halo out to 3.5 Mpc (P one).
- Radial spectral index steepening, radio emissivity ~10-42 ergs /s /cm^3 /Hz.
- Did testing on source subtraction vs masking sources on resultant halo spectrum. Also compared different centre points and sectors to see how susceptible to variation results were. There’s a significant variation.
- Observable extend is correlated to image depth + uv-coverage in relation to central brightness and enfolding radius. I.e. the other >2Mpc ones were bright halos, not necessarily unique.

https://www.thephysicsmill.com/2024/09/20/an-astrophysicist-attempts-to-measure-the-physics-of-outer-wilds/

Why CGS, but funny. 

# Maybe

https://arxiv.org/abs/2508.14019

Hubble tension increase a little when we did it this way.

https://arxiv.org/abs/2508.13267

We glued a ton of datasets together and made them slightly better.

https://arxiv.org/abs/2508.12556

Virial theorem + stellar mass vs halo mass or smth.

https://arxiv.org/abs/2508.15490 

Measure dust in galaxies using KIDS.

https://arxiv.org/abs/2508.06896

Galaxies again

https://arxiv.org/abs/2508.07232

Looks at stellar component to infer cluster boundary. 

https://arxiv.org/abs/2504.13380

Fits some good data by ignoring other data?

https://arxiv.org/abs/2406.00117

IDEK

# Boring

https://arxiv.org/abs/2508.15295

https://arxiv.org/abs/2508.07589