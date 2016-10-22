#! /usr/bin/env bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"
git reset --hard HEAD
git checkout develop
git pull
git clean -df
source venv/bin/activate
pip install .
cd chineurs/frontend
yarn install
npm run build
sudo systemctl restart chineurs-celery-dev.service
sudo systemctl restart chineurs-dev.service