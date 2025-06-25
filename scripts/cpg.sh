if [ -z "$1" ]; then
  echo "no code file provided"
  echo "Usage: $0 <code_file>"
  exit 1
fi

filepath="$1"

LD_LIBRARY_PATH=~/miniforge3/envs/cpg/lib/python3.12/site-packages/jep ../cpg/cpg-neo4j/build/install/cpg-neo4j/bin/cpg-neo4j --export-json ./out/cpg-export.json --no-neo4j "$filepath"
uv run src/json2dot.py ./out/cpg-export.json -o ./out/
