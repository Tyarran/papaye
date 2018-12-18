#!/bin/sh
source $(pipenv --venv)/bin/activate
exec "$@"
