#!/bin/bash

export CMD=${1}
if [ "${CMD}" == "" ]; then
  export CMD=minor
fi
docker run --rm -it -v $(pwd):/app -w /app treeder/bump --filename VERSION ${CMD}
export VERSION=$(cat VERSION)
echo ""
echo "Is this the right version? Type "yes" to continue packaging and upload to PyPI, or any other key to quit."
read line
if [ "${line}" != "yes" ]; then
  exit 0
fi
python setup.py sdist bdist_wheel
export TWINE_USERNAME=$(cat ${HOME}/pypiusername.txt)
export TWINE_PASSWORD=$(cat ${HOME}/testpypipassword.txt)
twine upload -r testpypi dist/*
export TWINE_PASSWORD=$(cat ${HOME}/pypipassword.txt)
twine upload dist/*

