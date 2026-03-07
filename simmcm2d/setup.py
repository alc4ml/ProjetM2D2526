from setuptools import setup, find_packages

setup(
    name='simmcm2d',
    version='0.0',
    description='Simulateur de maintenance prédictive',
    author='Marcels Company M2D',
    author_email='',
    packages=find_packages(),  # inclut simmcm2d.simmcm2d automatiquement
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "streamlit",
        "seaborn",
        "lifelines",
    ],
)