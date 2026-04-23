from setuptools import setup, find_packages

setup(
    name='summarize',
    version='2.0.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'summarize=summarize.interfaces.cli:main',
        ],
    },
)
