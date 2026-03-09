from setuptools import setup

setup(
   name='pipmcm2d',
   version='0.0',
   description='.',
   author='Marcels Company M2D',
   author_email='',
   packages=['pipmcm2d'],
   install_requires=[
      "numpy",
      "pandas",
      "joblib",
      # "simmcm2d",
      "matplotlib",
      "ipykernel"
   ],
)