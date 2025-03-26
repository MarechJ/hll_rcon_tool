#!/bin/bash
# entrypoint.sh


export TAGGED_VERSION=$(cat tag_version)
exec ./webhook-service