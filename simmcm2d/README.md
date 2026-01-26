Simulator Marcel's Company M2 des Données - SimMCM2D

This package contains the code necessary to install and utilize the simulator of several events regarding the specifications proposed.

## Installation/Requirements

The library can be easily installed using standard pip functionality. One is advised to consider installing the library in a new virtual environment, which can be created and activated as follows:

```
python3 -m venv env
source env/bin/activate 
```

Then, install the library as follows; observe that pip is responsible for installing the required dependencies previously specified in the file `setup.py`:

```
pip install path/to/simmcm2d
```

One can also consider installing the package in developper mode, so that new changes to the baseline code reflect directly in the installed package functionality:

```
pip install -e path/to/simmcm2d
```

Where `-e` or `--editable` stands for developpment mode, in which the source code can be edited.