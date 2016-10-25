#! /usr/bin/env bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"
git reset --hard HEAD
git checkout develop
git pull
git clean -df
