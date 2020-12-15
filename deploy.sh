#!/bin/bash
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

