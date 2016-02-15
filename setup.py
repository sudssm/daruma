from setuptools import setup, find_packages

setup(
    name="trustnoone",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PyNaCl==0.3.0",
        "secretsharing==0.2.6",
        "PyECLib==1.1.1",
        "uuid==1.30"
    ],
    extras_require={
        ':sys_platform == "darwin"': [
            'rumps==0.2.1'
        ]
    }
)
