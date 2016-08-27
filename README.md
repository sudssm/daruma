# Daruma [![Build Status](https://travis-ci.org/sudssm/daruma.svg?branch=master)](https://travis-ci.org/sudssm/daruma)

## Installation

### Command Line (OSX & Linux)
While in the project directory:

```
pip install --user -e . --process-dependency-links robustsecretsharing
```

To run the command line REPL:

```
python driver/daruma_cli.py
```

### GUI App (OSX only)
While in the project directory:

```
pip install --user -e \.\[gui] --process-dependency-links robustsecretsharing
python build.py
```
The newly built app will be in the `dist` directory.

### Dependencies
Daruma depends on libnacl, libffi, and liberasurecode. 

## Testing
`py.test` will automatically run all available test cases.

Note that on OSX, a system message may pop up saying "Python quit unexpectedly".  As long as the tests run to completion, this is expected and an indication of successful behavior.

## License
This software is licensed under the GPL license. If you would like an alternative license, please contact us.
