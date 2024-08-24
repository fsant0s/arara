import os
import platform

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

#with open("README.md", "r", encoding="UTF-8") as fh:
#    long_description = fh.read()

# Get the code version
#version = {}
#with open(os.path.join(here, "neuron/version.py")) as fp:
#    exec(fp.read(), version)
#__version__ = version["__version__"]


current_os = platform.system()

install_requires = [
    #TODO
]

setuptools.setup(
    name="neuron",
    #version=__version__,
    author="Fillipe Santos",
    author_email="fillipesantos00@gmail.com",
    description="NEURON - A Toolkit for Developing Recommender Systems Utilizing Large Language Model-Based Agents",
    #long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fsant0s/neuron",
    packages=setuptools.find_packages(include=["neuron*"], exclude=["test"]),
    install_requires=install_requires,
    #extras_require=extra_require,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    #python_requires=">=3.8,<3.13",
)
