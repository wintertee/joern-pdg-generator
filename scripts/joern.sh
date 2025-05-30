#!/bin/bash

if [ -z "$1" ]; then
  echo "no code file provided"
  echo "Usage: $0 <code_file>"
  exit 1
fi

filepath="$1"
filename=$(basename "$filepath")
lang="${filename##*.}"

echo "Processing file: $filepath"

mkdir -p ./out/joern
rm -rf ./out/joern/*

joern-parse "$filepath" > /dev/null 2>&1

for repr in all pdg cfg ast # ddg cdg pdg cpg14
do
    joern-export --repr="$repr" --out "./out/joern/$repr"
done

python src/merge.py \
    --cfg ./out/joern/cfg/* \
    --pdg ./out/joern/pdg/* \
    --ref ./out/joern/all/export.dot \
    --lang "$lang" \
    -o "./out/cdfg.dot"

python src/merge.py \
    --ast ./out/joern/ast/* \
    --cfg ./out/joern/cfg/* \
    --pdg ./out/joern/pdg/* \
    --ref ./out/joern/all/export.dot \
    --lang "$lang" \
    -o "./out/ast_cdfg.dot"

python src/filter.py ./out/joern/all/export.dot