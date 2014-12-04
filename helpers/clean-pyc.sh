#!/bin/bash
BASE_PATH=$(cd $(dirname $BASH_SOURCE)/.. && pwd)

find $BASE_PATH -name "*.pyc" -exec rm {} \;
find $BASE_PATH -name "*.pyo" -exec rm {} \;

