#!/bin/sh

ROOT=diamond/static

if [ "$1" = "watch" ]; then
  watch "sh $0" $ROOT --wait=1
else
  lessc $ROOT/diamond-ng.less $ROOT/diamond-ng.css
fi
