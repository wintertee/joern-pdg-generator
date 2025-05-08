#!/bin/bash

mkdir -p ./out
rm -r ./out/*

joern-parse examples/test.py

for repr in all pdg cfg ast #  ddg cdg  pdg cpg14
do
    joern-export --repr=$repr --out ./out/$repr
done

python src/merge.py --ast ./out/ast/* --cfg ./out/cfg/* --pdg ./out/pdg/* -r ./out/all/export.dot
python src/filter.py 