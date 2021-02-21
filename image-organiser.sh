#!/bin/bash

progress() {
	echo -en "\r$1/$2 files processed... ($3)"
}

cpfile() {	
	if [ "$TEST" == true ]; then
		cp --attributes-only $1 $2 >/dev/null 2>&1
	else
        # To speed up, only copy if file doesnt exist or has a size of zero.
        # We could use copy -n, to not overwrite files, but if test
        # function has been used, empty files will exist.
        if [[ ! -f "$2" || $(du "$2" | awk '{print $2}' ) == 0 ]]; then 
            cp "$1" "$2" 2>&1
        fi
	fi
}

CREATEDATESTRING="(20[0-9]{6}|[0-9]{4}-[0-9]{2}-[0-9]{2})"

while getopts r:t option
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
echo "Pre-transfer count of files in $DESTDIR/$ROOTDIR: $(find $DESTDIR/$ROOTDIR -type f | wc -l)"

for filePath in "${SOURCEFILES[@]}"
do
    fileName=${filePath##*/}
    createDate=$(grep -oE "$CREATEDATESTRING" <<< $fileName)
    if date -d $createDate >/dev/null 2>&1
    then
        month=$(date -d $createDate '+%b')
        year=$(date -d $createDate '+%Y')

        if [[ $fileName =~ .*\.(jpg|gif|png|jpeg) ]]
        then
            dir="$IMAGEDIR/$year/$month"
        elif [[ $fileName =~ .*\.(mp4) ]]
        then
            dir="$VIDEODIR/$year/$month"
        else
            dir="$MISCDIR"
        fi
        mkdir -p $dir
        cpfile "$filePath" "$dir/$fileName"
    else
        cpfile "$filePath" "$MISCDIR/$fileName"
    fi
    ((RUNNING_COUNT++))
    progress $RUNNING_COUNT $TOTAL_COUNT $fileName
done

echo -e "\nPost-transfer count of files in $DESTDIR/$ROOTDIR: $(find $DESTDIR/$ROOTDIR -type f | wc -l)"
echo ""
