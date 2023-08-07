#!/bin/bash
pushd /tmp/code/
git checkout refine-entrypoint-file
git pull
python -u python-image-organiser/processor.py $@
