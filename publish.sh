#!/bin/bash

#FROM PARAMETER
COMMIT_MESSAGE=$1

# COPYING THE FILES
git add *
git commit -m${COMMIT_MESSAGE}
git push
