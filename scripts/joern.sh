#!/bin/bash

lang=cpp

mkdir -p ./out/joern
rm -r ./out/joern/*

joern-parse examples/test.$lang > /dev/null 2>&1
for repr in all pdg cfg ast #  ddg cdg  pdg cpg14
do
    joern-export --repr=$repr --out ./out/joern/$repr
done

python src/merge.py --ast ./out/joern/ast/* --cfg ./out/joern/cfg/* --pdg ./out/joern/pdg/* --ref ./out/joern/all/export.dot --lang $lang -o $lang.dot

python -m xdot ./out/$lang.dot