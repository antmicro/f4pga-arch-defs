#!/bin/bash

usage() {
  if [ -n "$1" ]; then
    echo "$1" > /dev/stderr;
  fi
  echo "Usage: $0 [-c|-f]" > /dev/stderr
  exit 1
}

run() {
  eval $1
  res=$?
  if [[ $res != 0 ]]; then
    echo $2 > /dev/stderr
  fi
  return $res
}

check_file() {
  cmd=$1
  file=$2
  run "$cmd --inplace $file > /dev/null"
  if [[ `git status --porcelain`  ]]; then
     echo "verible needs to reformat $file"
     `git checkout -- $file`
     return 1
  else
     return 0
  fi
}

format_file() {
  cmd=$1
  file=$2
  run "$cmd --inplace $file" "verible failed to format $file"
  return $?
}

do_check=0
do_format=0

verible_exec=verible-verilog-format
while getopts "cf" opt; do
  case $opt in
    c)
      do_check=1;
      ;;
    f)
      do_format=1;
      ;;
    *)
      usage
      ;;
  esac
done
shift $((OPTIND - 1))

if (( do_check + do_format != 1 )); then
  usage "Provide exactly one option"
fi

ret=0
# using git will only check and format files in the git index. This avoids
# formatting temporary files and files in submodules
TOP_DIR=`git rev-parse --show-toplevel`
for file in $(git ls-tree --full-tree --name-only -r HEAD | grep "tests" | grep "\.v$"); do
  if [ $do_check != 0 ]; then
    check_file $verible_exec $TOP_DIR/$file;
    res=$?
  elif [ $do_format != 0 ]; then
    format_file "$verible_exec" $TOP_DIR/$file;
    res=$?
  fi;

  if [[ $res != 0 ]]; then
    ((ret++))
  fi
done

exit $ret
