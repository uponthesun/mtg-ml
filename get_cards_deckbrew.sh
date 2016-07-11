#! /bin/bash

# Gets magic card data in JSON format from deckbrew: https://deckbrew.com/api/
# Takes in an optional argument which is the query string to use.

queryString=$1;
page=1;

echo "["

response="initial placeholder value";
while [ 1 ]
do
    response=`curl -s "http://api.deckbrew.com/mtg/cards?page=$page&$queryString"`;
    if [ "$response" == "[]" ]
        then
            break;
    fi

    # http://askubuntu.com/questions/89995/bash-remove-first-and-last-characters-from-a-string/90235#90235
    trimmedResponse=${response:1:${#response}-2}
    if [ $page != 1 ]
        then
            trimmedResponse=", $trimmedResponse"
    fi
    echo $trimmedResponse;
    page=$((page + 1));
done

echo "]"