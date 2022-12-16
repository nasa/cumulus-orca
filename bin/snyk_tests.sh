#!/bin/bash
## =============================================================================
## NAME: snyk_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Scans the ORCA project with snyk for vulnerabilities.
## Install snyk in Mac using:
## brew tap snyk/tap
## brew install snyk
##
## ENVIRONMENT SETTINGS
## -----------------------------------------------------------------------------
## SNYK_AUTHENTICATION_TOKEN (str) - snyk authentication token found from Snyk UI browser https://app.snyk.io/account.
## export locally first using:
## export SNYK_AUTHENTICATION_TOKEN=<YOUR_TOKEN>
## -----------------------------------------------------------------------------

# authenticate snyk CLI locally
snyk auth $SNYK_AUTHENTICATION_TOKEN

# Iac run limited to 20 runs a month. TBD Discuss with Jon Velapondi.
# echo "Scanning Infrastructure as code with Snyk for potential vulnerabilities..."
# snyk iac test || true

# scan orca website
echo "Scanning open-source code with Snyk for potential vulnerabilities..."
cd website
snyk test -d --severity-threshold=high || true

# TODO: scan orca lambdas