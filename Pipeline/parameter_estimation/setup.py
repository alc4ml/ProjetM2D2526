from setuptools import setup, find_packages

setup(
    name="parameter_estimation",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
    ],
)