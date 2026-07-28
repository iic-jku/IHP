#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <folder_or_file> [folder_or_file ...]"
  exit 1
fi

gds_files=()

for input_path in "$@"; do
  if [ -d "$input_path" ]; then
    while IFS= read -r file; do
      gds_files+=("$file")
    done < <(find "$input_path" -maxdepth 1 -type f -iname "*.gds" | sort)
  elif [ -f "$input_path" ]; then
    gds_files+=("$input_path")
  else
    echo "Skipping: $input_path (not a valid file/folder)"
  fi
done

if [ "${#gds_files[@]}" -eq 0 ]; then
  echo "No .gds files found in provided inputs."
  exit 1
fi

for gds in "${gds_files[@]}"; do
  echo "=============================="
  echo "Running simulation for: $gds"
  echo "=============================="

  "$SCRIPT_DIR/run_sim.sh" "$gds"
done

python3 "$SCRIPT_DIR/combine_snp.py" "$@"
