#!/usr/bin/env bash


for FILE in input/pagecontent/*.xml; do
    DIR=$(dirname $FILE)
    BASE=$(basename -s .xml $FILE)
    echo $BASE
    OUTFILE="$DIR/$BASE.md"
    echo $OUTFILE
    CONTENT=$(xmllint --xpath  "/*[local-name()='div']/child::* | /*[local-name()='div']/text()" $FILE)
    echo "$CONTENT" > "$OUTFILE"
    rm $FILE
done

for FILE in input/pagecontent/*.md; do
    CONTENT=$(sed  's/<h3>\(.*\)<\/h3>/### \1/' $FILE |   sed  's/<h4>\(.*\)<\/h4>/#### \1/' |  sed  's/<h5>\(.*\)<\/h5>/##### \1/'   )
    echo "$CONTENT" > "$FILE"
done


for FILE in input/pagecontent/*.md; do
    if  ! [ -f "$FILE" ]; then
	continue
    fi
    if  [ "$FILE"  == "input/pagecontent/full_contents.md" ]; then
	continue
    fi

    #trim leading space and get first line
    HEAD=$(sed -z 's/^\s*//; s/\s*$//'  $FILE | head -1)
    if [[ $HEAD  =~ ^\s*(\#\#\#\#*)(.*)$ ]]; then
	# echo "${BASH_REMATCH[1]}: $FILE is OK. Title: ${BASH_REMATCH[2]}"
	continue;
    fi
    if [[ $HEAD  =~ ^\s*(\#+)(.*)$ ]]; then
	echo "WARNING: ${BASH_REMATCH[0]}: $FILE is has too short headers "
	echo "   ${BASH_REMATCH[0]}: ${BASH_REMATCH[2]}"
	echo "   <$HEAD>"
    elif [[ $HEAD  =~ ^\s*(.*)$ ]]; then
	echo "WARNING: $FILE has no headers: ${BASH_REMATCH[1]}"
	echo "    <$HEAD>"
	if [[ $HEAD  =~ (.*) ]]; then
	    echo "    Stuff:${BASH_REMATCH[1]}:"
	fi

    else	    
	echo "WARNING: $FILE is NOT OK: Empty contents"
    fi
done


