#!/bin/bash
#
# Project Wok
#
# Copyright IBM, Corp. 2015
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301USA

mkdir -p venv

HAVE_UNITTEST=yes
PYTHON_VER=2.7

# Verify if the required commands exists on the system
command -v virtualenv >/dev/null 2>&1 || { echo >&2 "virtualenv must be installed for your distribution.  Aborting."; exit 1; }
command -v pip >/dev/null 2>&1 || { echo >&2 "pip must be installed for your distribution.  Aborting."; exit 1; }

# Get absolute path of this script
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
reqfile=$SCRIPTPATH'/requirements.txt'

# Start the virtual environment
virtualenv venv --no-site-packages


# Actiate the virtual environment
source venv/bin/activate

while read line; do

  case "$line" in
    \#*)
    continue ;; # skip comments
    "")
    continue ;; # skip empty lines
    *)
    venv/bin/python$PYTHON_VER -c "import $line" > /dev/null 2>&1
    status=$?
    if [ $status -ne 0 ]; then
        pip install -r $reqfile # Install the required modules to run tests
        break
    fi
  esac
done < $reqfile

# Execute the test suite
#python registered_tests.py
#nosetests --with-html --html-file=test_report.html registered_tests.py

if [ "$1" = "-v" ]; then
    OPTS="-v"
    shift
else
    OPTS=""
fi

if [ $# -ne 0 ]; then
    ARGS="$@"
else
    ARGS=`find -name "fvt_*.py" | xargs -I @ basename @ .py`
fi

if [ "$HAVE_UNITTEST" != "yes" -o "$PYTHON_VER" == "2.6" ]; then
    CMD="unit2"
else
    CMD="python -m unittest"
fi

LIST=($ARGS)
FVT_LIST=()
for ((i=0;i<${#LIST[@]};i++)); do
    FVT_LIST+=(${LIST[$i]})
done
PYTHONPATH=../ $CMD $OPTS ${FVT_LIST[@]}

# Deativate the virtual environment
deactivate

rm -fr venv
