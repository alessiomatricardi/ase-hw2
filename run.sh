#!/usr/bin/env bash
pip3 install -r requirements.txt # --ignore-installed
python -m spacy download en

export FLASK_APP=monolith
export FLASK_ENV=development
export FLASK_DEBUG=true

mkdir monolith/static/attachments
mkdir monolith/static/pictures
flask run --host 0.0.0.0