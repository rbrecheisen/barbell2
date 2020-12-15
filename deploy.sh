#!/bin/bash
which twine
if [ "$?" == "1" ]; then
  echo "You do not seem to have Twine installed (wrong venv?). It is needed to upload to PyPI"
  echo "Type 'install' to install it and continue or any other key to quit"
  read line
  if [ "${line}" != "install" ]; then
    exit 0
  fi
  python -m pip install twine
fi
if [ ! -f "${HOME}/pypiusername.txt" ]; then
  echo "Could not find ${HOME}/pypiusername.txt"
  exit 0
fi
if [ ! -f "${HOME}/pypipassword.txt" ]; then
  echo "Could not find ${HOME}/pypipassword.txt"
  exit 0
fi
export CMD=${1}
if [ "${CMD}" == "" ]; then
  export CMD=minor
fi
docker run --rm -it -v $(pwd):/app -w /app treeder/bump --filename VERSION ${CMD}
export VERSION=$(cat VERSION)
echo ""
echo "Is this the right version? Type "yes" to continue, or any other key to quit."
read line
if [ "${line}" != "yes" ]; then
  exit 0
fi
git status
echo "Everything ready to be pushed to Git? Type "yes" to continue, or any other key to quit."
read line
if [ "${line}" != "yes" ]; then
  exit 0
fi
echo "Type your Git commit message here below"
read message
git add -A
git commit -m "Saving version ${VERSION} before deploying to PyPI. ${message}"
git push
python setup.py sdist bdist_wheel
export TWINE_USERNAME=$(cat ${HOME}/pypiusername.txt)
export TWINE_PASSWORD=$(cat ${HOME}/pypipassword.txt)
twine upload dist/*

