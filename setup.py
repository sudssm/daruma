from setuptools import setup, find_packages
import sys

# Base settings required for CLI and GUI setup
base_setup = dict(
    name="trustnoone",
    version="0.1",
    setup_requires=[],
    packages=find_packages(),
    include_package_data=True,
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
    }
)

# General settings needed for app builds
build_setup = {}

# Platform-specific build setup
if sys.platform == "darwin":
    base_setup["setup_requires"].extend([
        "py2app==0.10"
    ])

    build_setup.update(
        app=["gui/sb_gui.py"],
        data_files=["gui/webview_server/templates", 'gui/webview_server/static'],
        options={
            "py2app": {
                "optimize": 2,
                "packages": ['jinja2', 'flask'],
                "plist": {
                    "LSUIElement": True,
                }
            }
        }
    )

# Combine it all
base_setup.update(build_setup)
setup(
    **base_setup
)
