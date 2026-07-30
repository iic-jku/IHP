#!/bin/bash

# input argument
GDS_FILE="$1"

# strip extension -> folder name
BASENAME="${GDS_FILE%.*}"

echo "GDS file   : $GDS_FILE"
echo "Folder name: $BASENAME"

# create palace config file
python3 palace_auto_sim.py "$GDS_FILE"

# change directory and run palace
cd "${BASENAME}/palace_auto_sim_data" || exit 1
# MPI ranks: half the cores, less headroom for other users of the big shared
# machines. That formula goes <1 on anything below 26 cores and would silently pin
# long sims to a single rank, so fall back to plain half-the-cores there.
NP=${PALACE_NP:-$(( $(nproc) - 4 ))}
(( NP < 1 )) && NP=$(( ($(nproc)+1)/2 ))
(( NP < 1 )) && NP=1
palace -np "$NP" config.json

# create S-Parameter files
cd ..
cd ..


echo "${BASENAME} completed."
