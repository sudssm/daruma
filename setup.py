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
        "robustsecretsharing==0.1"
    ],
    dependency_links=[
        "git+ssh://git@github.com/michsoch/robust-secret-sharing.git@sss#egg=robustsecretsharing-0.1"
    ]

)
