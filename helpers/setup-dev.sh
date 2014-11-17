#!/bin/bash
BASE_PATH=$(cd $(dirname $BASH_SOURCE)/.. && pwd)

. ~/ve/iCE/bin/activate
export PYTHONPATH="$PYTHONPATH:$BASE_PATH"
export ICE_CONFIG_PATHS="$BASE_PATH/config/default:$BASE_PATH/config/local"
