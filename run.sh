#! /usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )" 
source venv/bin/activate
gunicorn chineurs.main:APP -b 0.0.0.0:5000
