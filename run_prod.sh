#! /usr/bin/env bash

set -e

SOCKET_FILE=$1

cd "$( dirname "${BASH_SOURCE[0]}" )" 
source venv/bin/activate
yoyo apply
gunicorn chineurs.main:APP -b unix:$SOCKET_FILE --error-logfile - --log-file -
