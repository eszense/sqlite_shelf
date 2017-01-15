from setuptools import setup, find_packages

setup(
    name='sqlite_shelf',
    version='0.0.1',
    description='2-D dict-like object backed by Sqlite',
    author='eszense',
    classifiers=['Programming Language :: Python :: 3.5'],
    packages=find_packages(exclude=['tests*']),
    install_requires=['es_commons']
)
