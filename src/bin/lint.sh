#!/usr/bin/env bash

set -e -o pipefail

function cd_to_source_directory() {
  cd `dirname ${0}`/..
}

function run_linter() {
  echo "linting: ${1}"
  p run pylint ${1}
  echo "sorting imports: ${1}"
  p run isort --profile=black --check-only ${1}
  echo "formatting: ${1}"
  p run black --check  ${1} --diff
  echo "check types: ${1}"
  p run mypy ${1} --ignore-missing-imports
  echo "scanning vulnerabilities: ${1}"
  p run bandit -r ${1} -s B608
}

cd_to_source_directory

source bin/shared.sh

echo "Running linters"
run_linter pfcli
echo "Finished linters"
