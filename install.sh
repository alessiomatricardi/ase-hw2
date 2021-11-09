#!/usr/bin/env bash

echo 'Install requirements'
pip3 install -r requirements.txt
echo 'Download spacy en'
python3 -m spacy download en && echo 'Setup done!' || echo 'Download failed'