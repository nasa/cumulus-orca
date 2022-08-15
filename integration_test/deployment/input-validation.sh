#!/bin/bash
set -ex

# Negated REGEX that checks that the PREFIX is alpha numeric with no spaces and the optional use of an _
if [[ ! ${bamboo_PREFIX} =~ ^[[:upper:][:lower:][:digit:]_]+$ ]]; then
    echo "FATAL: PREFIX variable value [${bamboo_PREFIX}] is invalid. Only alpha numeric values and _ are allowed."
    exit 1
fi