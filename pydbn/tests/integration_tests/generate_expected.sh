#!/usr/bin/env sh

# Will run dbn for each - run this in the integration_tests directory
# first arg is path to dbn script
find `pwd` -type d -mindepth 1 | xargs -I DIRECTORY env DBN_LOAD_PATH=DIRECTORY python $1 -f DIRECTORY/expected.bmp DIRECTORY/code.dbn
