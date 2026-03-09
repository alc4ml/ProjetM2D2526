# Pipeline of Marcel's Company M2 des Données - PipMCM2D

This library contains the necessary functionalities for a complete process of analisys and policy optimization for fleet manutention. It makes use of the library `SimMCM2D`.

## Installation/Requirements

The library can be easily installed using standard pip functionality. One is advised to consider installing the library in a new virtual environment, which can be created and activated as follows:

```
python3 -m venv env
source env/bin/activate 
```

Then, install the library as follows; observe that pip is responsible for installing the required dependencies previously specified in the file `setup.py`:

```
pip install path/to/pipmcm2d
```

One can also consider installing the package in developper mode, so that new changes to the baseline code reflect directly in the installed package functionality:

```
pip install -e path/to/pipmcm2d
```

Where `-e` or `--editable` stands for developpment mode, in which the source code can be edited.

Important: The library `SimMCM2D` must also be installed for stachastic policy optimization.

## Functionalities Exported

The functions exported are the following, for parametric estimation:

 * `estimate_inspection_parameters(df)`: returns estimations for `mu` and `sigma`
 * `estimate_component_parameters(df)`: returns estimations for `eta` and `beta`
 * `estimate_parameters(df)`: returns all parameters estimated
 * `estimate_parameters_filepath(filepath)`: returns all parameters estimated from a csv sample filepath

And the following for policy optimization using Genetic Algorithms:

 * `compute_cost`: computes the average cost function using Monte-Carlo
 * `algorithme_genetique`: optmizes the policy using Genetic Algorithms

## File Examples and Notebook

In the `pipmcm2d/examples` path, one can find some library use examples, as follows:

 * `parameter_estimator.ipynb`: simple examples on the use of the functionalities for parametric estmatin
 * `AG_Optimisation.ipynb`: an example of policy optimization using Genetic Algorithms