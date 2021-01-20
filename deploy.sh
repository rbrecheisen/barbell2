#!/bin/bash

# Check if Twine is installed for uploading the package
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

# Check if we have credential files (username and password) for uploading to PyPI
if [ ! -f "${HOME}/pypiuser.txt" ]; then
  echo "Could not find ${HOME}/pypiuser.txt"
  exit 0
fi
if [ ! -f "${HOME}/pypipassword.txt" ]; then
  echo "Could not find ${HOME}/pypipassword.txt"
  exit 0
fi

# Process command-line argument. Should either be -h for help or indicator how to upgrade
# the version number (patch, minor, major). Anything else is an error.
export CMD=${1}
if [ "${CMD}" == "-h" ]; then
    echo "Usage: deploy.sh [patch|minor|major]"
    exit 0
fi
if [ "${CMD}" != "" ] && [ "${CMD}" != "patch" ] && [ "${CMD}" != "minor" ] && [ "${CMD}" != "major" ]; then
    echo "Illegal argument ${CMD}"
    exit 1
fi
if [ "${CMD}" == "" ]; then
  export CMD=minor
fi

# Upgrade version number
docker run --rm -it -v $(pwd):/app -w /app treeder/bump --filename VERSION ${CMD}
export VERSION=$(cat VERSION)
echo ""
echo "Is this the right version? Type "yes" to continue, or any other key to quit."
read line
if [ "${line}" != "yes" ]; then
  exit 0
fi

# Check git status
git status
echo "Everything ready to be pushed to Git? Type "yes" to continue, or any other key to quit."
read line
if [ "${line}" != "yes" ]; then
  exit 0
fi

# Commit to git if there have been changes
echo "Type your Git commit message here below"
read message
git add -A
git commit -m "Saving version ${VERSION} before deploying to PyPI. ${message}"
git push
if [ "$?" == "1" ]; then
    echo "Something went wrong with pushing to Git. Please revert back to previous VERSION"
    exit 1
fi

# Clean up build directories for deployment
rm -rf build dist

# Build new package and upload to PyPI
python setup.py sdist bdist_wheel
export TWINE_USERNAME=$(cat ${HOME}/pypiuser.txt)
export TWINE_PASSWORD=$(cat ${HOME}/pypipassword.txt)
twine upload dist/*
