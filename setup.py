from setuptools import setup, find_packages

setup(
    name="trustnoone",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    setup_requires=[
        "py2app"
    ],
    install_requires=[
        "PyNaCl==1.0.1",
        "PyECLib==1.2.0",
        "uuid==1.30",
        "robustsecretsharing==0.1",
        "colorama==0.2.5"
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
    },
    app=["gui/sb_gui.py"],
    data_files=["gui/webview_server/templates", 'gui/webview_server/static'],
    options=dict(py2app=dict(packages=['jinja2', 'flask']))
)
