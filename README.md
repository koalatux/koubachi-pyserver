# About this Project

The Koubachi Sensor is a small battery powered device, that measures
soil moisture, light intensity and temperature, measurements are then
transmitted via W-LAN to a server. Koubachi Sensors were sold until 2015
and the original Koubachi servers are about to be retired soon.

This project aims to replace the original Koubachi server with a bridge,
that forwards measurements to a custom MQTT or REST end point, such that
the Koubachi Sensors can still be operated when the original servers got
shut down.

# Installation

Running the koubachi-pyserver requires Python 3.7. On a Raspberry Pi
running Raspbian Buster this comes pre-installed but git won't be
available by default:

```bash
sudo apt install git
```

koubachi-pyserver uses `pipenv` for dependency management and virtual
environments. Make sure that `pip` and  `pipenv` are installed. Note:
the following does a user installation to prevent breaking any
system-wide packages. If pipenv isn't available in your shell after
installation, you’ll need to add the user base's binary directory to
your PATH

```bash
sudo apt install python3-pip
pip3 install -U pipenv
export PATH=$PATH:$HOME/.local/bin
```
 
Download the [latest
release](https://github.com/koalatux/koubachi-pyserver/releases) or
clone the master branch with Git as shown below. Then, create a virtual
environment with `pipenv` and install all project dependencies:

```bash
git clone https://github.com/koalatux/koubachi-pyserver.git
cd koubachi-pyserver/
pipenv install
```

Now you need a `config.yml` that contains the encryption key and
calibration settings for your Koubachi Sensors. This information can be
downloaded from [Koubachi Labs](https://labs.koubachi.com).

# Running

To launch the server, run the following command:

```bash
pipenv shell
python src/server.py
```

# Reconfigure Sensor

Read in the [API
documentation](https://github.com/koubachi-sensor/api-docs#change-the-sensors-server-address)
how to reconfigure your sensor to connect to your own server.
