import setuptools

with open("README.md", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="ollie-assistant",
    version="1.0.0",
    packages=setuptools.find_packages(),
    description="A Snips-based voice assistant for oscilloscopes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jwmilson/ollie",
    install_requires=[
        "paho-mqtt",
        "python-usbtmc",
        "pyusb",
        "spidev",
    ],
    entry_points={
        "console_scripts": ["ollie = ollie.__main__:main"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Scientific/Engineering",
    ],
)
