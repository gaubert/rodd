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

W=`convert $in -format %w info:`
H=`convert $in -format %h info:`

if [ "$W" -gt "$H" ]; then
   echo "Width is greater than Height"
   #resize image and border of 25x25
   $convert $in -normalize -resize '420x>' -bordercolor White -border 12x12 dummy.jpg
   W=`convert dummy.jpg -format %w info:`
   echo "original W=$W"
   if [ "$W" -lt "200" ]; then
	   W=200
   else
	   W=$(($W-30))
   fi
   # add side border to put the text
   echo "final W=$W"
   # add side border to put the text
   $convert dummy.jpg -gravity east -splice "$W"x0 -background White -append temp.png
else
   echo "Width is not greater than Height"
   $convert $in -normalize -resize 'x420>' -bordercolor White -border 12x12 dummy.jpg
   W=`convert dummy.jpg -format %w info:`
   echo "original W=$W"
   if [ "$W" -lt "200" ]; then
	   W=200
   else
	   W=$(($W-20))
   fi
   # add side border to put the text
   $convert dummy.jpg -gravity east -splice "$W"x0 -background White -append temp.png
fi
newsize=`convert dummy.jpg -format %wx%h info:`
echo "resized imaged size="$newsize

# crop to keep balanc in the postcard
#$convert $in -normalize -resize x640 -resize '640x<' -resize 50% -gravity center -crop 640x480+0+0 +repage -bordercolor White -border 12x12 dummy.jpg
#get width and height of the produced picture
#W=`convert dummy.jpg -format %w info:`
#echo "W is $W"
H=`convert temp.png -format %h info:`

# create a mask fro rounding the borders
# apply the mask
#create mvg mask
$convert temp.png -format 'roundrectangle 1,1 %[fx:w+4],%[fx:h+4] 12,12' info: > rounded_corner.mvg
$convert temp.png -border 3 -alpha transparent -background none -fill white -stroke none -strokewidth 0 -draw "@rounded_corner.mvg" rounded_corner_mask.png
$convert temp.png -matte -bordercolor none -border 3 rounded_corner_mask.png -compose DstIn -composite temp.png 
# add drop shadow
$convert temp.png \( +clone -background black -shadow 80x3+20+20 \) +swap -background white -layers merge +repage shadow.png 
newsize=`convert shadow.png -format %wx%h info:`
echo "resized imaged size="$newsize
#cp shadow.png /homespace/gaubert/Dev/projects/rodd/etc/img-manip
#create label and add it with composite

#$convert -font $IMG_MANIP_HOME/fonts/Candice.ttf  -pointsize 36 label:"$text" label.png 
##$convert -font $IMG_MANIP_HOME/fonts/Candice.ttf -size 350x"$H" -gravity center -pointsize 36 label:"$text" label.png

#label size: remove the 50 pixels corresponding to the borders
W=$(($W-50))
H=$(($H-50))
echo "WxH = $W x $H"
$convert -font /homespace/gaubert/.gimp-2.6/plug-ins/fonts/Candice.ttf -size "$W"x"$H" label:"$text" label.png
cp label.png /homespace/gaubert/Dev/projects/rodd/etc/img-manip
#when we have a label without any size
#$composite label.png -gravity south -geometry +0+52 shadow.png out.png

$composite label.png -gravity east -geometry +90+0 shadow.png out.png
cp out.png $out

#rm -Rf $working_dir



