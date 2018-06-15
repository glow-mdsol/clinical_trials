from setuptools import setup

setup(
    name='clinical_trials',
    version='0.1',
    packages=['clinical_trials', 'tests'],
    install_requires=['requests', 'glom', 'xmlschema'],
    url='https://github.com/glow-mdsol/clinical_trials',
    license='MIT',
    author='glow-mdsol',
    author_email='glow@mdsol.com',
    description='A simple tool for processing CT.gov records'
)
