# Daruma [![Build Status](https://travis-ci.org/sudssm/daruma.svg?branch=master)](https://travis-ci.org/sudssm/daruma)

## Overview
Cloud storage is ubiquitous in our everyday lives. Businesses and consumers use services like Dropbox, Google Drive, and Box to store a wide variety of important documents, ranging from family photos to healthcare information and proprietary corporate data. However, users rarely consider the possibility of these services experiencing failures. What happens if their provider goes down or gets hacked? For many, the consequences would be catastrophic.

All cloud providers make assurances of data safety, security, and availability. However, these cannot be guaranteed because providers are a single point of failure, vulnerable to everything from hackers and software flaws to state-level intervention.

Daruma solves these problems by eliminating the need to trust any cloud provider.  It combines and secures the storage of existing providers by running advanced cryptographic and redundancy algorithms on users’ computers.  With no single point of failure, we make a simple but previously unattainable guarantee: no provider can read, corrupt, or delete your files -- ever.

Further, Daruma achieves this in an intuitive, familiar interface. Once a user logs in with their existing provider accounts, Daruma handles everything automatically - no new passwords or different workflows.  When a provider fails, Daruma identifies the issue and fully recovers, without interrupting the user’s workflow. 

Best of all, Daruma is highly space efficient and is faster and more scalable than using cloud providers in isolation. Daruma handles the complexities of security and reliability for users, allowing them to confidently utilize cloud storage without worrying about its previously inherent risks.

## Installation
Currently, the Daruma executable (with all GUI features) only supports OSX El Capitan. Users of other Linux-based operating systems can use the command line version, or attempt to build their own executable. Daruma currently doesn't support Windows because one of our dependencies (liberasurecode) doesn't compile on Windows.

### Command Line (OSX & Linux)
Install dependencies - Python 2.7, Pip, libnacl, libffi, haveged, liberasurecode.
On Ubuntu, these needed libraries can be installed with
```
echo "deb http://archive.ubuntu.com/ubuntu trusty-backports main restricted universe multiverse" | sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get -y install libnacl-dev libffi-dev haveged liberasurecode-dev
```

While in the project directory:
```
pip install --user . --process-dependency-links robustsecretsharing
```

### Building the GUI Application (Tested on OSX El Capitan)
While in the project directory:

```
pip install --user -e \.\[gui] --process-dependency-links robustsecretsharing
python build.py
```
The newly built app will be in the `dist` directory.

## Running

### GUI
Simply execute the packaged Daruma executable.  To see status badges in the OSX Finder, you may need to explicitly enable the app as a Finder Extension, which can be done in the Extensions pane of System Preferences.

### Command Line
To run the command line REPL:

```
python driver/daruma_cli.py
```
Type 'help' to get started. 'add' will allow you to add new providers, 'provision' will create a new Daruma instance from the providers added, and 'load' will load an existing Daruma instance from the providers.

## Testing
`py.test` will automatically run all available test cases.

Note that on OSX, a system message may pop up saying "Python quit unexpectedly".  As long as the tests run to completion, this is expected and an indication of successful behavior.

## License
This software is licensed under the GPL license. If you would like an alternative license, please contact us.
