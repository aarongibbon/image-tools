#!/bin/bash
pushd /tmp/code/
git pull
git checkout refine-entrypoint-file
python python-image-organiser/processor.py
