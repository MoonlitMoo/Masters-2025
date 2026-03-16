# Install notes

# Casa

[https://casadocs.readthedocs.io/en/stable/notebooks/introduction.html#Prerequisite-OS-Libraries](https://casadocs.readthedocs.io/en/stable/notebooks/introduction.html#Prerequisite-OS-Libraries)

Make sure these libraries exist

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install imagemagick -y  # ImageMagick package
sudo apt install xvfb -y  # Xvfb (X virtual framebuffer)
sudo apt install gfortran -y  # GNU Fortran (alternative to compat-libgfortran-48)
sudo apt install libnsl2 -y  # Newer version of libnsl
sudo apt install libcanberra-gtk-module -y  # libcanberra-gtk2 equivalent
sudo apt install fuse -y  # Filesystem in Userspace
sudo apt install perl -y  # Perl interpreter
```

Download from https://casa.nrao.edu/casa_obtaining.shtml, then untar with

```bash
tar -xvf <filename>.tar.xz
```

Add command to terminal with

```bash
echo 'export PATH=$PATH:/path/to/casa-<version>/bin' >> ~/.bashrc
source ~/.bashrc
```

# Carta

## Installation

[https://cartavis.org/#download](https://cartavis.org/#download)

```bash
sudo add-apt-repository ppa:cartavis-team/carta
sudo apt-get update
sudo apt install carta
```

## Usage

```bash
carta
carta <image>.image --no-browser
```