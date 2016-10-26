#! /usr/bin/env bash

set -e

export NVM_DIR="/home/jonathan/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm

source venv/bin/activate
pip install .
cd chineurs/frontend
yarn install
npm run build
sudo systemctl restart chineurs-celery-dev.service
sudo systemctl restart chineurs-dev.service
