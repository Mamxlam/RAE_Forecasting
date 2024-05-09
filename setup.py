from setuptools import setup

setup(
   name='RAE_Forecasting',
   version='0.1',
   description='Module for Greek Regulatory Authority of Energy, on Renewable Energy Permits Forecasting.',
   author='Mamxlam',
   author_email='mmalamat@csd.auth.gr',
   packages=['RAE_Forecasting'],  #same as name
#    install_requires=['wheel', 'bar', 'greek'], #external packages as dependencies
   scripts=[
            'tools/'
           ]
)