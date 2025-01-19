#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
set -o monitor
set -o noglob

# calculate the current directory
SCRIPT_DIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")
declare -r SCRIPT_DIR

# calculate the package directory
PACKAGE_DIR=$(dirname -- "${SCRIPT_DIR}")
declare -r PACKAGE_DIR

# python environment
export PYTHONPATH="${PACKAGE_DIR}/src"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# run script
conda run --no-capture-output --live-stream --name telegpt --cwd "${PACKAGE_DIR}/src" \
    python telegpt.py \
        "$@"
