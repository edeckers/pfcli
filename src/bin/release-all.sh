#!/usr/bin/env bash

function cd_to_root_directory () {
  cd `dirname ${0}`/../../
}

function set_github_actions_git_details () {
  git config --local user.name ${GITHUB_RELEASE_USER_NAME}
  git config --local user.email ${GITHUB_RELEASE_USER_EMAIL}
}

function publish_semantic_release () {
  echo "Publishing release"

  set_github_actions_git_details

  echo "Running semantic-release version"
  version_result=`p run semantic-release version 2>&1`
  error_code=`echo $?`
  is_error_code=`[ ${error_code} -ne 0 ] && echo 1 || echo 0`
  
  no_release_count=`echo "${version_result}" | grep -cim1 "no release"`
  is_release=`[ ${no_release_count} -eq 0 ] && echo 1 || echo 0`

  echo "${version_result}"

  if [[ ${is_error_code} -eq 1 || ${is_release} -ne 1 ]]; then
    echo "has error code: ${is_error_code}"
    echo "is release created: ${is_release}"

    echo "Received error code or no release was created. Aborting."
    exit 0
  fi
  echo "Ran semantic-release version"

  echo "Running semantic-release publish"
  p run semantic-release publish
  echo "Ran semantic-release publish"

  echo "Releasing to PyPI"
  POETRY_PYPI_TOKEN_PYPI=${PYPI_TOKEN} p publish
  echo "Released to PyPI"

  echo "Published release"
}

cd_to_root_directory

source src/bin/shared.sh

publish_semantic_release
