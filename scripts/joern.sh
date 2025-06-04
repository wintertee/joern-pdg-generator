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

joern-parse "$filepath"

if [ $? -ne 0 ]; then
  echo "joern-parse failed"
  exit 1
fi

for repr in all pdg cfg ast cpg14 # ddg cdg pdg 
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

python ./src/v2.py ./out/joern/all/export.dot --cfg ./out/joern/cfg/* --lang "$lang"

python ./src/v2.py ./out/joern/all/export.dot --cfg ./out/joern/cfg/* --lang "$lang" --ast -o ./out/ast_v2.dot

# python src/visualization.py ./out/joern/all/export.dot