from setuptools import setup, find_packages

setup(
    name="trustnoone",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PyNaCl==1.0.1",
        "PyECLib==1.2.0",
        "uuid==1.30",
        "robustsecretsharing==0.1",
        "colorama==0.2.5",
        "requests==2.9.0",
        "Flask==0.10.1"
    ],
    dependency_links=[
        "git+ssh://git@github.com/michsoch/robust-secret-sharing.git@sss#egg=robustsecretsharing-0.1"
    ],
    extras_require={
        "gui": [
            "flask>=0.10.1",
            "wxPython==3.0.2.0",
            "wxPython-common==3.0.2.0"
        ],
        ":sys_platform == 'darwin'": [
            'pyobjc==3.0.4'
        ]
    }
)
