## Installation

Running the koubachi-pyserver requires Python 3.7. On a Raspberry Pi running Raspbian Buster this comes pre-installed
but git won't be available by default:
```bash
sudo apt install git
```

koubachi-pyserver uses `pipenv` for dependency management and virtual environments. Make sure that `pip` and  `pipenv`
are installed. Note: the following does a user installation to prevent breaking any system-wide packages. If pipenv 
isn’t available in your shell after installation, you’ll need to add the user base’s binary directory to your PATH

```bash
sudo apt install python3-pip
pip3 install -U pipenv
export PATH=$PATH:$HOME/.local/bin
```
 
Download the [latest release](https://github.com/koalatux/koubachi-pyserver/releases)
or clone the master branch with Git as shown below. Then, create a virtual environment with
`pipenv` and install all project dependencies:
```bash
git clone https://github.com/koalatux/koubachi-pyserver.git
cd koubachi-pyserver/
pipenv install
```

Now you need a ```config.yml``` that contains the encryption key and calibration settings for your Koubachi sensors. This
information can be downloaded from [Koubachi Labs](https://labs.koubachi.com).

## Running ##

To launch the server, run the following command:
```bash
pipenv shell
python src/server.py
```
