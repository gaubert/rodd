#!/bin/bash
set -x

cat text_data.txt |
while read width gravity color pointsize font x y text
  do
    convert -size ${width}x -gravity $gravity -fill $color -font ${font} -background wheat \
            -pointsize $pointsize  -page +${x}+${y}  label:"${text}"  miff:-
  done | convert -size 269x394  xc:   -   -flatten    text_layered.jpg
