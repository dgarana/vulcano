from setuptools import setup, find_packages
from os import path
from io import open

import vulcano


HERE = path.abspath(path.dirname(__file__))


with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='vulcano',
    version=vulcano.__version__,
    description='A sample Python project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dgarana/vulcano',
    author='The Python Packaging Authority',
    author_email='pypa-dev@googlegroups.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='sample setuptools development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
