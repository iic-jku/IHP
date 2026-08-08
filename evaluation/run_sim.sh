#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# input argument
GDS_FILE="$1"

# strip extension -> folder name
BASENAME="${GDS_FILE%.*}"

# palace_sim.py names the model after the GDS file, so the data directory,
# the Palace output directory and the .sNp all carry MODEL rather than the script name
MODEL="$(basename "$BASENAME")"

echo "GDS file   : $GDS_FILE"
echo "Folder name: $BASENAME"

# create palace config file
python3 "$SCRIPT_DIR/palace_sim.py" "$GDS_FILE"

# change directory and run palace
cd "${BASENAME}/${MODEL}_data" || exit 1
# MPI ranks: half the cores, less headroom for other users of the big shared
# machines. That formula goes <1 on anything below 26 cores and would silently pin
# long sims to a single rank, so fall back to plain half-the-cores there.
NP=${PALACE_NP:-$(( $(nproc)))}
(( NP < 1 )) && NP=$(( ($(nproc)+1)/2 ))
(( NP < 1 )) && NP=1
palace -np "$NP" config.json

# create S-Parameter files
cd ..
cd ..


echo "${BASENAME} completed."
