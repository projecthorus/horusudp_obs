# Horus UDP OBS-Studio Overlay Generator
This GUI listens for Horus UDP Packets, and displays them on a GUI which can be used with [OBS-Studio](https://obsproject.com) to provide a overlay of payload statistics.

### Authors
* Mark Jessop <vk5qi@rfhead.net>

## Dependencies

### Install Python Dependencies
```console
$ pip install -r requirements.txt
```

### Grab this Repo
```console
$ git clone https://github.com/projecthorus/horusudp_obs.git
$ cd horusudp_obs
```

## Usage

### Starting GUI
```console
$ python -m horusobs.gui --callsign HORUSBINARY
```

### Using with OBS-Studio
TBD