# Daruma [![Build Status](https://travis-ci.com/sudssm/daruma.svg?token=9r7x75stRuvJScvvvedh&branch=master)](https://travis-ci.com/sudssm/daruma)

## Installation

### Command Line (OSX & Linux)
While in the project directory:

```
pip install --user -e . --process-dependency-links robustsecretsharing
```
(Note: this assumes that ssh keys are configured for git)

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

## Testing
`py.test` will automatically run all available test cases.

Note that on OSX, a system message may pop up saying "Python quit unexpectedly".  As long as the tests run to completion, this is expected and an indication of successful behavior.
