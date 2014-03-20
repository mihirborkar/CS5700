#!/bin/sh
FILE1=$( md5sum $1 |awk '{print $1 }' )
FILE2=$( md5sum $2 |awk '{print $1 }' )
if [ $FILE1 = $FILE2 ]
    then echo "Same";
else echo "Different";
fi
