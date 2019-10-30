# About this Project

The Koubachi Sensor is a small battery powered device, that measures
soil moisture, light intensity and temperature, measurements are then
transmitted via W-LAN to a server. Koubachi Sensors were sold until 2015
and the original Koubachi servers retired in October 2019.

This project aims to replace the original Koubachi server with a bridge,
that forwards measurements to a custom MQTT or REST end point, such that
the Koubachi Sensors can still be operated when the original servers got
shut down.

# Installation

## Using Dependencies from Debian

koubachi-pyserver can be run using only dependencies available in
Debian buster. Run the following commands to install all the required
packages and clone the repository:

### Installing

```bash
sudo apt install git python3 python3-yaml python3-flask python3-paho-mqtt python3-cryptography
git clone https://github.com/koalatux/koubachi-pyserver.git
cd koubachi-pyserver
```

### Running

First read about configuration below, then to launch the server, run the
following command:

```bash
PYTHONPATH=$PYTHONPATH:src python3 -m koubachi_pyserver.app
```

## Using Pipenv

### Installing

Running the koubachi-pyserver requires Python 3.7. On a Raspberry Pi
running Raspbian Buster this comes pre-installed but git won't be
available by default:

```bash
sudo apt install git
```

koubachi-pyserver can use `pipenv` for dependency management and virtual
environments. Make sure that `pip` and  `pipenv` are installed. Note:
the following does a user installation to prevent breaking any
system-wide packages. If pipenv isn't available in your shell after
installation, you’ll need to add the user base's binary directory to
your PATH:

```bash
sudo apt install python3-pip
pip3 install -U pipenv
PATH=$PATH:$HOME/.local/bin
```
 
Download the [latest
release](https://github.com/koalatux/koubachi-pyserver/releases) or
clone the master branch with Git as shown below. Then, create a virtual
environment with `pipenv` and install all project dependencies:

```bash
git clone https://github.com/koalatux/koubachi-pyserver.git
cd koubachi-pyserver
pipenv install
```

### Running

First read about configuration below, then to launch the server, run the
following command:

```bash
pipenv run python -m koubachi_pyserver.app
```

# Configuration

Now you need a `config.yml` that contains the encryption keys and
calibration data for your Koubachi Sensors. Write an e-mail to
[sensors@koubachi.com](mailto:sensors@koubachi.com) and mention the MAC
addresses of your Koubachi Sensors. Within a few days someone will reply
with the required data.

Configuration is work in progress. Please refer to the [issues
page](https://github.com/koalatux/koubachi-pyserver/issues) if you would
like to help contributing.

# Reconfiguring the Koubachi Sensor

Read in the [API
documentation](https://github.com/koubachi-sensor/api-docs#change-the-sensors-server-address)
how to reconfigure your Koubachi sensor to connect to your own server.

# Development

Install development dependencies:

```bash
pipenv install --dev
```

## Static Type Checking and Tests

Perform static type checking:

```bash
pipenv run mypy --strict src
```

Run tests:

```bash
pipenv run pytest
```
