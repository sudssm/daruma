# trust-no-one [![Build Status](https://travis-ci.com/sudssm/trust-no-one.svg?token=9r7x75stRuvJScvvvedh&branch=master)](https://travis-ci.com/sudssm/trust-no-one)

## Installation

### Command Line (OSX & Linux)
While in the project directory:

```
pip install --user -e . --process-dependency-links robustsecretsharing
```
(Note: this assumes that ssh keys are configured for git)

To run the command line REPL:

```
python driver/sb_cli.py
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
