#!/bin/sh
# Based on https://exyr.org/2011/inotify-run/
FORMAT=$(echo -e "\033[1;33m%w%f\033[0m written")
make dirhtml
while inotifywait -qre close_write --format "$FORMAT" --exclude _build .
do
    make dirhtml
done
