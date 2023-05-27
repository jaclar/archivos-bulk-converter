#!/bin/sh

TMPDIR=`mktemp -d`
WMTMPDIR=`mktemp -d`

INPUT=$1
OUTPUT=$2
WM=$3

if [ ! -d "$INPUT" ]; then
    echo "Input Directory: '$INPUT' doesn't exist"
    exit 1
fi

# if [ ! $(ls -U $INPUT/*.tif 1> /dev/null 2>&1) ]; then
#     echo "Input Directory: '$INPUT' doesn't contain any *.tif files."
#     exit 1
#fi

if [ ! -f "$WM" ]; then
    echo "Watermark file: '$WM' doesn't exist"
    exit 1
fi

DOC=`basename "$INPUT"`

echo "Generating from $INPUT:  $OUTPUT/$DOC.pdf"

convert "$INPUT/*.tif" -quality 30% "$TMPDIR/page-%04d.jpeg"

for FILE in $(ls $TMPDIR/page-*.jpeg)
do
    JPEG=`basename $FILE`
    echo $JPEG
    composite -watermark 30 -gravity center \
        "$WM" \
        "$TMPDIR/$JPEG" \
        "$WMTMPDIR/$JPEG"
done

convert "$WMTMPDIR/*.jpeg" "$OUTPUT/$DOC.pdf"

rm -rf $TMPDIR
rm -rf $WMTMPDIR
