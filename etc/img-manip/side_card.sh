#!/bin/bash
set -x

IMG_MANIP_HOME=/homespace/gaubert/Dev/projects/rodd/etc/img-manip
IMAGEMAGICK_DIR=/homespace/gaubert/ImageMagick-6.6.9-8
#IMAGEMAGICK_DIR=/usr

font_dir=$IMG_MANIP_HOME/fonts/

convert=$IMAGEMAGICK_DIR/bin/convert
composite=$IMAGEMAGICK_DIR/bin/composite

in=$1
out=$3
text=$2

usage="./side_card.sh input_file \"My text to add\" output_file"

if [ -z "$in" ]; then
  echo "in is not defined"
fi

#################################
## if $1 is relative,
## build the absolute path
#################################
D=`dirname "$1"`
B=`basename "$1"`
in="`cd \"$D\" 2>/dev/null && pwd || echo \"$D\"`/$B"

#################################
## if $3 is relative,
## build the absolute path
#################################
D=`dirname "$3"`
B=`basename "$3"`
out="`cd \"$D\" 2>/dev/null && pwd || echo \"$D\"`/$B"

working_dir=/tmp/wrk_dir
mkdir -p $working_dir

rm -f out.jpg
cd $working_dir

W=`convert dummy.jpg -format %w info:`
H=`convert temp.jpg -format %h info:`

if [ "$W" -gt "$H" ]; then
   echo "Width is greater than Height"
   #resize image and border of 25x25
   $convert $in -normalize -resize 320x240^ -bordercolor White -border 12x12 dummy.jpg
else
   echo "Width is not greater than Height"
   $convert $in -normalize -resize 240x320^ -bordercolor White -border 12x12 dummy.jpg
fi


#resize image and border of 25x25
#$convert $in -normalize -resize 300x400^ -bordercolor White -border 12x12 dummy.jpg
#$convert $in -resize x160 -resize '160x<' -resize 50% -gravity center -crop 80x80+0+0 +repage dummy.jpg
$convert $in -normalize -bordercolor White -border 12x12 dummy.jpg
# add bigger bottom border
$convert dummy.jpg -gravity east -splice 350x0 -background White -append temp.jpg
#get width and height of the produced picture
#W=`convert dummy.jpg -format %w info:`
#echo "W is $W"
H=`convert temp.jpg -format %h info:`

# create a mask fro rounding the borders
# apply the mask
#create mvg mask
$convert temp.jpg -format 'roundrectangle 1,1 %[fx:w+4],%[fx:h+4] 12,12' info: > rounded_corner.mvg
$convert temp.jpg -border 3 -alpha transparent -background none -fill white -stroke none -strokewidth 0 -draw "@rounded_corner.mvg" rounded_corner_mask.png
$convert temp.jpg -matte -bordercolor none -border 3 rounded_corner_mask.png -compose DstIn -composite temp.png 
# add drop shadow
$convert temp.png \( +clone -background black -shadow 80x3+20+20 \) +swap -background white -layers merge +repage shadow.png 
#cp shadow.png /home/aubert/Dev/projects/rodd/etc/img-manip
#cp shadow.png /home/aubert/Dev/projects/rodd/etc/img-manip
cp shadow.png /homespace/gaubert/Dev/projects/rodd/etc/img-manip
#create label and add it with composite

#$convert -font $IMG_MANIP_HOME/fonts/Candice.ttf  -pointsize 36 label:"$text" label.png 
##$convert -font $IMG_MANIP_HOME/fonts/Candice.ttf -size 350x"$H" -gravity center -pointsize 36 label:"$text" label.png

#label size: remove the 50 pixels corresponding to the borders
#W=$(($W-50))
#$convert -font /homespace/gaubert/.gimp-2.6/plug-ins/fonts/Candice.ttf -gravity center -size "$W"x60 label:"$text" label.png
#when we have a label without any size
#$composite label.png -gravity south -geometry +0+52 shadow.png out.png

##$composite label.png -gravity east -geometry +0+0 shadow.png out.png
cp out.png $out

#rm -Rf $working_dir



