#!/bin/bash
set -x

cat text_data.txt |
while read width gravity color  pointsize x y text
  do
    convert -size ${width}x -gravity $gravity -fill $color -background wheat \
            -pointsize $pointsize  -page +${x}+${y}  label:"${text}"  miff:-
  done | convert -size 200x100 xc:   -   -flatten    text_layered.jpg
