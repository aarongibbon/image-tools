#!/bin/bash

progress() {
	echo -en "\r$1/$2 files processed... ($3)"
}

cpfile() {	
	if [ "$TEST" == true ]; then
		cp --attributes-only $1 $2 >/dev/null 2>&1
	else	
        cp $1 $2 2>&1
	fi
}

CREATEDATESTRING="(20[0-9]{6}|[0-9]{4}-[0-9]{2}-[0-9]{2})"

while getopts s:d:t option
do
        case "$option"
        in
            r) ROOTDIR="${OPTARG}/";;
            t) TEST=true;;
		
        esac
done

if [ $(( $# - $OPTIND + 1 )) != 2 ]; then
    echo "Usage: `basename $0` [options] SOURCEDIRECTORY DESTINATIONDIRECTORY"
    exit 1
fi

SOURCEDIR=${@:$OPTIND:1}
DESTDIR=${@:$OPTIND+1:1}

readarray -d '' SOURCEFILES < <(find $SOURCEDIR -type f -print0)

TOTAL_COUNT=${#SOURCEFILES[@]}

RUNNING_COUNT=0

IMAGEDIR="$DESTDIR/${ROOTDIR}images"
VIDEODIR="$DESTDIR/${ROOTDIR}videos"
MISCDIR="$DESTDIR/${ROOTDIR}misc"

mkdir -p $IMAGEDIR
mkdir -p $VIDEODIR
mkdir -p $MISCDIR

echo ""
echo "Pre-transfer count of files in $DESTDIR: $(find $DESTDIR -type f | wc -l)"

IFS=';'

for file in "${SOURCEFILES[@]}"
do
    FILE=${file##*/}
    CREATEDATE=$(grep -oE "$CREATEDATESTRING" <<< $IMAGE)
    if date -d $CREATEDATE >/dev/null 2>&1
    then
        month=$(date -d $CREATEDATE '+%b')
        year=$(date -d $CREATEDATE '+%Y')

        if [[ $file =~ .*\.(jpg|gif|png|jpeg) ]]
        then
            dir="$IMAGEDIR/$YEAR/$MONTH"
        elif [[ $file =~ .*\.(mp4) ]]
        then
            dir="$VIDEODIR/$YEAR/$MONTH"
        else
            dir="$MISCDIR"
        fi
        mkdir -p $dir
        cpfile $file $dir
    else
        cpfile $file "$MISCDIR"
    fi
    ((RUNNING_COUNT++))
    progress $RUNNING_COUNT $TOTAL_COUNT ${file##*/}
done

echo -e "\nPost-transfer count of files in $DESTDIR""media/"": $(find $DESTDIR -type f | wc -l)"
echo ""
