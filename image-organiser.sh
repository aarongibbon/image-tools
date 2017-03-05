#!/bin/bash


ROOTDIR="."

while getopts d:t option
do
        case "${option}"
        in
                d) ROOTDIR=${OPTARG};;
                t) TEST=true;;
        esac
done

progress() {
	echo -en "\r$1/$2 files processed..."
}

cpfile() {	
	if [ "$TEST" == true ]; then
		cp --attributes-only $1 $2 >/dev/null 2>&1
	else	
		cp $1 $2 >/dev/null 2>&1
	fi
}

IMAGES=$(find $ROOTDIR -regex ".*\.\(jpg\|gif\|png\|jpeg\)")
VIDEOS=$(find $ROOTDIR -regex ".*\.\(mp4\)")
OTHER=$(find $ROOTDIR -not -regex ".*\.\(jpg\|gif\|png\|jpeg\|mp4\)" | tail -n +2)

#IMAGES_COUNT=${#IMAGES[@]}
IMAGES_COUNT=$(wc -w <<< $IMAGES)
VIDEO_COUNT=$(wc -w <<< $VIDEOS)
OTHER_COUNT=$(wc -w <<< $OTHER)

TOTAL_COUNT=$(($IMAGES_COUNT + $VIDEO_COUNT + $OTHER_COUNT))
RUNNING_COUNT=0

ROOTFOLDER="media"
IMAGEFOLDER="$ROOTFOLDER/images"
VIDEOFOLDER="$ROOTFOLDER/videos"
MISCFOLDER="$ROOTFOLDER/misc"

mkdir -p $IMAGEFOLDER
mkdir -p $VIDEOFOLDER
mkdir -p $MISCFOLDER

for i in $IMAGES
do
	IMAGE=${i##*/}
	CREATEDATE=$(grep -o "20[0-9]\{6\}" <<< $IMAGE)
	if date -d $CREATEDATE >/dev/null 2>&1
	then
		MONTH=$(date -d $CREATEDATE '+%b')
		YEAR=$(date -d $CREATEDATE '+%Y')
		FOLDER="$IMAGEFOLDER/$YEAR/$MONTH"
		mkdir -p $FOLDER
		cpfile $i $FOLDER
	else
		cpfile $i "$MISCFOLDER"
	fi
	((RUNNING_COUNT++))
	progress $RUNNING_COUNT $TOTAL_COUNT
done

for i in $VIDEOS
do
	cpfile $i "$VIDEOFOLDER"
	((RUNNING_COUNT++))
	progress $RUNNING_COUNT $TOTAL_COUNT
	
done

for i in $OTHER
do
	cpfile $i "$MISCFOLDER"
	((RUNNING_COUNT++))
	progress $RUNNING_COUNT $TOTAL_COUNT
done

echo ""
