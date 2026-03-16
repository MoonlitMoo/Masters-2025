# Setup notes

# VUW VPN

Cisco anyconnect designed for Ubuntu 18.04, not 24.04. Can work around by doing following as [reddit post](https://www.reddit.com/r/Ubuntu/comments/1dd1qxz/libwebkit2gtk4037_is_not_available_on_ubuntu_2404/) says. 

```python
sudo nano /etc/apt/sources.list
```

Paste `deb [http://gb.archive.ubuntu.com/ubuntu](http://gb.archive.ubuntu.com/ubuntu) jammy main` and save. Then run

```python
sudo apt update
sudo apt install libwebkit2gtk-4.0-dev
sudo apt --fix-broken install
```

The update will complain about half a dozen things, but can be probably safely ignored as you can now connect via [`vpn.vuw.ac.nz`](http://vpn.vuw.ac.nz). Note that [`vpn.wtgn.ac.nz`](http://vpn.wtgn.ac.nz) doesn’t connect which is what the email told me to use (first comes from student access email).

# SOLAR drives

Add some things to allow the mounting.

```python
sudo apt update
sudo apt install cifs-utils smbclient
```

Setup share location and a mounting script

```python
mkdir -p ~/vuw_share
```

```bash
#!/bin/bash

MOUNTPOINT="/home/benja/vuw_share"
SHARE="//vuwstocoissrin1.vuw.ac.nz/SCPS_BC_01"

if ! mountpoint -q "$MOUNTPOINT"; then
  echo "Mounting VUW share..."
    sudo mount -t cifs "$SHARE" "$MOUNTPOINT" -o credentials=/etc/smbcredentials/vuw,uid=1000,vers=3.0,sec=ntlmssp
else
  echo "Already mounted."
fi

```

Then setup the credentials file

```bash
sudo mkdir -p /etc/smbcredentials
sudo nano /etc/smbcredentials/vuw
```

with the following info

```bash
username=colquhbe@staff.vuw.ac.nz
password=YourPassword
```

Do the same for `vuw_local` but ignore the domain name.

and rewrite perms to require sudo

```bash
sudo chmod 600 /etc/smbcredentials/vuw; sudo chown root:root /etc/smbcredentials/vuw
```

## Archive Image folders

# RAAPOI

- I still have access to raapoi via `colquhbenj` account
- I can access SOLAR via `smbclient //vuwstocoissrin1.vuw.ac.nz/SCPS_BC_01 --user colquhbe@staff.vuw.ac.nz --workgroup STAFF`
    - More details [here](https://vuw-research-computing.github.io/raapoi-docs/external_providers/#storage-for-learning-and-research-solar-vuw-high-capacity-storage)

## Copy from onedrive

```bash
rclone copy onedrive:Documents/Processed\ Masters\ Data/25A-157.sb47896587.eb48188930.60749.83678572917.tar.gz . --progress
```

## Copy to SOLAR

```bash
smbclient "//vuwstocoissrin1.vuw.ac.nz/SCPS_BC_01" --user="colquhbe@staff.vuw.ac.nz" --workgroup="STAFF" --command="prompt OFF; cd \"Processed-data/24A-411.sb45152540.eb45209965.60336.070794328705\"; put 24A-411.sb45152540.eb45209965.60336.070794328705.tar.gz"
```