#!/bin/bash

CURRENT_DATE=$(date -I | cut -d'T' -f1)

for file in _posts/*.md; do
  # Extract the date part of the filename
  FILENAME=$(basename "$file")
  POST_DATE_STR=$(echo "$FILENAME" | cut -d'-' -f1-3)
  
  # Convert to seconds since epoch for comparison
  # The -j flag is for BSD date, which is what's on macOS.
  POST_DATE_SEC=$(date -j -f "%Y-%m-%d" "$POST_DATE_STR" "+%s" 2>/dev/null)
  
  # If the above command fails, it's not a valid date, so skip it.
  if [ -z "$POST_DATE_SEC" ]; then
    continue
  fi
  
  CURRENT_DATE_SEC=$(date -j -f "%Y-%m-%d" "$CURRENT_DATE" "+%s")

  if [ "$POST_DATE_SEC" -gt "$CURRENT_DATE_SEC" ]; then
    NEW_FILENAME=$(echo "$FILENAME" | sed "s/$POST_DATE_STR/$CURRENT_DATE/")
    echo "Renaming $FILENAME to $NEW_FILENAME"
    mv "_posts/$FILENAME" "_posts/$NEW_FILENAME"
  fi
done
