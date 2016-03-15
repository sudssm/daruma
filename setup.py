from setuptools import setup, find_packages

setup(
    name="trustnoone",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PyNaCl==0.3.0",
        "secretsharing==0.2.6",
        "PyECLib==1.1.1",
        "uuid==1.30",
        "dropbox==4.0",
        "appdirs==1.4.0"
    ]
)
