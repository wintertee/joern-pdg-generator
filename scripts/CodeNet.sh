#! /bin/bash

# download Project_CodeNet_C++1000.tar.gz and extract it under ./data/Project_CodeNet_C++1000

lang=cpp
path=./data/Project_CodeNet_C++1000

for file in $path/*/*.$lang; do
    echo "Processing $file"
    mkdir -p ./out/joern
    rm -r ./out/joern/*
    
    joern-parse "$file" > /dev/null 2>&1
    for repr in all pdg cfg ast #  ddg cdg  pdg cpg14
    do
        joern-export --repr=$repr --out ./out/joern/$repr
    done
    
    python ./src/v2.py ./out/joern/all/export.dot --cfg ./out/joern/cfg/* --lang "$lang"

    python ./src/v2.py ./out/joern/all/export.dot --cfg ./out/joern/cfg/* --lang "$lang" --ast -o ./out/ast_v2.dot
    
done