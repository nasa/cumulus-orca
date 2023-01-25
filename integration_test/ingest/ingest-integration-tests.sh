#!/bin/bash
# Sets up TF files in a consistent manner.
# todo: Is all this needed? Theoretically, should be able to delete everything referenced in the state.
set -ex

aws s3 ls