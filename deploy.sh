#! /usr/bin/env bash

set -e

source venv/bin/activate
pip install .
cd chineurs/frontend
yarn install
npm run build
sudo systemctl restart chineurs-celery-dev.service
sudo systemctl restart chineurs-dev.service
