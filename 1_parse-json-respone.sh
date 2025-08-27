#!/bin/bash

LIST=(0 1 2 3 4 5 6 7 8 9)

for i in "${LIST[@]}"
do
    echo "I'm writing the $i item ..."
    echo "##############################"
    curl -s -H "User-Agent:Chrome/133.0" https://www.sahamyab.com/guest/twiter/list?v=0.1 | jq ".items[$i]" > ./"$(date +%s).json"
    echo "Done for the $i item..."
    echo "##############################"
    sleep 5
done
   