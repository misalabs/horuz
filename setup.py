from setuptools import setup, find_packages

setup(
    name='horuz',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'yaspin',
        'elasticsearch==7.5.1',
        'tabulate==0.8.7',
        'requests==2.23.0',
        'dpath==2.0.1',
    ],
    entry_points='''
        [console_scripts]
        hz=horuz.cli:cli
    ''',
)
