#!/bin/bash
BASE_PATH=$(cd $(dirname $BASH_SOURCE)/.. && pwd)

. ~/ve/iCE/bin/activate
export PYTHONPATH="$PYTHONPATH:$BASE_PATH"
export ICE_CONFIG_PATH="$BASE_PATH/etc"
