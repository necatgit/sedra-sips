#!/bin/bash
# usage: nd.sh kaspadDir sedraDir file
sed -e 's#sedracoin/sedrad#kaspanet/kaspad#g' "$2/$3" | diff --strip-trailing-cr -U1 "$1/$3" - 
