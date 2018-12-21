#!/bin/bash

pushd sam-app

# Pip is broken on the mac and -t does not work
# So we need to use this workaround
echo "[install]
prefix=" > ~/.pydistutils.cfg

# HeyDJ function
pushd notifier
mkdir -p build
cp *.py build
if [ -e "requirements.txt" ]; then
  pip install -r requirements.txt -t ./build
fi
popd

# All done, return back to where we were
rm -f ~/.pydistutils.cfg
popd