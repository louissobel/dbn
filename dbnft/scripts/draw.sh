set -e

# $1 is input file
# $2 is output file
# debug / verbose is on
base=$(basename $1)
python ../pydbn/dbn.py $1 --evm --verbose > artifacts/intermediate_ethasm/drawings/draw-script-temp.ethasm
make artifacts/drawings/draw-script-temp.ethasm
echo "ethasm in artifacts/drawings/draw-script-temp.ethasm"

hh assemble-and-run \
	--file artifacts/drawings/draw-script-temp.ethasm \
	--debug \
	--output-file $2

open $2
