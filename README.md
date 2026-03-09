# Predictive Maintenance Simulator – M2 Mathematics of Data

This repository contains the work developed for the **M2 Mathématiques des Données project**.  
The objective is to simulate the degradation and maintenance of a fleet of components, generate synthetic datasets, analyze them, and estimate the underlying parameters.

The project combines **simulation, statistical analysis, parameter estimation, and an interactive web interface**.

---

## Project Structure

- **simmcm2d** – Simulation library for fleet degradation and maintenance events  
- **pipmcm2d** – Pipeline for parameter estimation and policy optimization  
- **Pipeline** – Implementation of the full pipeline and Streamlit application  
- **Analysis** – Notebooks for data analysis and experimentation  
- **outputs** – Generated datasets and simulation outputs  
- **Livrables** – Project deliverables (reports, presentation, documentation)  
- **requirements.txt** – Python dependencies  
- **README.md** – Project documentation  
---

## Main Components

### simmcm2d
A Python package implementing the **simulator of component degradation and maintenance events**.  
It allows generating datasets and computing key performance indicators (KPIs).

### pipmcm2d
A Python package implementing the **analysis pipeline**, including:

- parameter estimation from simulated datasets
- optimization of maintenance policies using **genetic algorithms**

This package builds on top of the simulator.

### Streamlit Application

An interactive web interface was developed using **Streamlit** to allow users to:

- configure simulation parameters
- generate datasets
- visualize KPIs and descriptive statistics
- estimate parameters from the generated data

The application is accessible online:

https://projetm2d2526-m2d.streamlit.app/

---

## Installation

Create a virtual environment and install the required dependencies:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
**Contributors** : 

Project developed by the Marcel's Company – M2 Mathématiques des Données team.
