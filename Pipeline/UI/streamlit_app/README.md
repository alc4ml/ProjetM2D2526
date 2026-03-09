# Streamlit User Interface

This directory contains the **interactive web interface** of the project, developed using Streamlit.  
The application allows users to configure simulation parameters, generate datasets, analyze results, and estimate model parameters.

---

## Technologies

The user interface was developed using **Streamlit**, a Python framework for building interactive web applications for data science projects.

The application is implemented in **Python** and uses libraries such as **pandas** for data manipulation and visualization libraries to display simulation results and descriptive analyses.

This technology enables the development of a **lightweight and interactive interface** where users can configure parameters, run simulations, and analyze the generated data.

---

## Application Architecture

The application follows a **modular architecture**.

The main entry point is:

**app.py : **

This file manages the navigation between the different pages of the interface.

Each page is implemented in a separate module located in the **`views`** directory.

The interface is organized into four main pages:

- **Configuration** – define the parameters used for the simulation  
- **Simulation** – generate datasets based on the chosen parameters  
- **Descriptive Analysis** – visualize KPIs and statistical summaries  
- **Estimation** – estimate the parameters of the model from the generated dataset  

---

## How to Access the Interface

There are two ways to use the application.

### 1. Run Locally

Clone the repository:
```bash
git clone https://github.com/alc4ml/ProjetM2D2526.git
```
Then run the Streamlit application:

```bash
streamlit run Pipeline/UI/streamlit_app/app.py
```
---

### 2. Access Online

The application is deployed and accessible online:

https://projetm2d2526-m2d.streamlit.app/
