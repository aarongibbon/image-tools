#!/bin/bash
pushd /tmp/code/
git checkout refine-entrypoint-file
git pull
python python-image-organiser/processor.py $@
