# trust-no-one [![Build Status](https://travis-ci.com/sudssm/trust-no-one.svg?token=9r7x75stRuvJScvvvedh&branch=master)](https://travis-ci.com/sudssm/trust-no-one)

## Installation

### OS X & Linux
While in the project directory: `pip install --user -e . --process-dependency-links robustsecretsharing`
Note: this assumes that ssh keys are configured for git

## Run UI
See instructions in `driver/sb_ui.py`

## Testing
`py.test` will automatically run all available test cases.

Note that on OSX, a system message may pop up saying "Python quit unexpectedly".  As long as the tests run to completion, this is expected and an indication of successful behavior.
