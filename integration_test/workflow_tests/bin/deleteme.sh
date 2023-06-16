#!/bin/bash

export bamboo_PREFIX='doctest'
export orca_BUCKETS='{"protected": {"name": "'$bamboo_PREFIX'-protected", "type": "protected"}, "internal": {"name": "'$bamboo_PREFIX'-internal", "type": "internal"}, "private": {"name": "'$bamboo_PREFIX'-private", "type": "private"}, "public": {"name": "'$bamboo_PREFIX'-public", "type": "public"}, "orca_default": {"name": "'$bamboo_PREFIX'-orca-primary", "type": "orca"}}'

echo $orca_BUCKETS