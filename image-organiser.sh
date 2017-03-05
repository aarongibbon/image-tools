#!/bin/bash

progress() {
	echo -en "\r$1/$2 files processed..."
}

IMAGES=$(find $1 -regex ".*\.\(jpg\|gif\|png\|jpeg\)")
OTHER=$(find $1 -not -regex ".*\.\(jpg\|gif\|png\|jpeg\)" | tail -n +2)

#IMAGES_COUNT=${#IMAGES[@]}
IMAGES_COUNT=$(wc -w <<< $IMAGES)
OTHER_COUNT=$(wc -w <<< $OTHER)

TOTAL_COUNT=$(($IMAGES_COUNT + $OTHER_COUNT))
RUNNING_COUNT=0
mkdir -p photos
mkdir -p photos/misc

for i in $IMAGES
do
	IMAGE=${i##*/}
	CREATEDATE=$(grep -o "20[0-9]\{6\}" <<< $IMAGE)
	if date -d $CREATEDATE >/dev/null 2>&1
	then
		MONTH=$(date -d $CREATEDATE '+%b')
		YEAR=$(date -d $CREATEDATE '+%Y')
		FOLDER="photos/$YEAR/$MONTH"
		mkdir -p $FOLDER
		cp $i $FOLDER >/dev/null 2>&1
	else
		cp $i "photos/misc" >/dev/null 2>&1
	fi
	((RUNNING_COUNT++))
	progress $RUNNING_COUNT $TOTAL_COUNT
done

for i in $OTHER
do
	cp $i "photos/misc" >/dev/null 2>&1
	((RUNNING_COUNT++))
	progress $RUNNING_COUNT $TOTAL_COUNT
done

echo ""
