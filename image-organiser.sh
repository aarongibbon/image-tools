#!/bin/bash


ROOTDIR="."
CREATEDATESTRING="(20[0-9]{6}|[0-9]{4}-[0-9]{2}-[0-9]{2})"
while getopts s:d:t option
do
        case "${option}"
        in
                s) ROOTDIR=${OPTARG};;
		d) DESTDIR=${OPTARG};;
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

IMAGES=$(find $ROOTDIR -regex ".*\.\(jpg\|gif\|png\|jpeg\)" -printf '%p;')
VIDEOS=$(find $ROOTDIR -regex ".*\.\(mp4\)" -printf '%p;')
OTHER=$(find $ROOTDIR -not -regex ".*\.\(jpg\|gif\|png\|jpeg\|mp4\)" -type f -printf '%p;' | tail -n +2)

#IMAGES_COUNT=${#IMAGES[@]}
IMAGES_COUNT=$(echo $IMAGES | sed 's/;/\n/g' | head -n -1 | wc -l)
VIDEO_COUNT=$(echo $VIDEOS | sed 's/;/\n/g' | head -n -1 | wc -l)
OTHER_COUNT=$(echo $OTHER | sed 's/;/\n/g' | head -n -1 | wc -l)

TOTAL_COUNT=$(($IMAGES_COUNT + $VIDEO_COUNT + $OTHER_COUNT))
RUNNING_COUNT=0

pushd $DESTDIR 1>/dev/null
ROOTFOLDER="media"
IMAGEFOLDER="$ROOTFOLDER/images"
VIDEOFOLDER="$ROOTFOLDER/videos"
MISCFOLDER="$ROOTFOLDER/misc"

mkdir -p $IMAGEFOLDER
mkdir -p $VIDEOFOLDER
mkdir -p $MISCFOLDER

echo ""
echo "Pre-transfer count of files in $DESTDIR""media/"": $(find $DESTDIR -type f | wc -l)"

IFS=';'

for i in $IMAGES
do
	IMAGE=${i##*/}
	CREATEDATE=$(grep -oE "$CREATEDATESTRING" <<< $IMAGE)
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

echo -e "\nPost-transfer count of files in $DESTDIR""media/"": $(find $DESTDIR -type f | wc -l)"
echo ""
