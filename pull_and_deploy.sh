#! /usr/bin/env bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"
./pull.sh
./deploy.sh
