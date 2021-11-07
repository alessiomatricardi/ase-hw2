#!/usr/bin/env bash

export FLASK_APP=monolith
export FLASK_ENV=development
export FLASK_DEBUG=true

rm -rf monolith/static/attached
mkdir monolith/static/attached
flask run --host 0.0.0.0