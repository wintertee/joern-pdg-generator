#!/bin/bash

mkdir -p ./out
rm -r ./out/*

joern-parse examples/test.java
for repr in all pdg cfg ast #  ddg cdg  pdg cpg14
do
    joern-export --repr=$repr --out ./out/$repr
done

python src/merge.py --ast ./out/ast/* --cfg ./out/cfg/* --pdg ./out/pdg/* --ref ./out/all/export.dot --lang java
# python src/filter.py 
python -m xdot ./out/merged.dot