if [ -z "$1" ]; then
  echo "no code file provided"
  echo "Usage: $0 <code_file>"
  exit 1
fi

filepath="$1"

/home/wintertee/cpg/cpg-neo4j/build/install/cpg-neo4j/bin/cpg-neo4j --export-json cpg-export.json --no-neo4j "$filepath"
mv cpg-export.json ~/testjoern/examples/test.json
uv run src/json2dot.py
uv run xdot output_graph.dot