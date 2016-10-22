#! /usr/bin/env bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"
source venv/bin/activate
export FLASK_APP=chineurs.main:APP
export FLASK_DEBUG=true
yoyo apply
celery -A chineurs.celery worker &
CELERY_PID=$!
cd chineurs/frontend
npm start &
WEBPACK_PID=$!
cd ../..
flask run
trap 'kill CELERY_PID;kill $WEBPACK_PID' SIGINT
