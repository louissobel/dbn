set -e

BIN_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


PROJECT_ROOT=$(dirname $BIN_DIR)
OUTPUT_FILE="$PROJECT_ROOT/evm_compile_lambda.zip"
PYDBN_BASE="$PROJECT_ROOT/pydbn"


set -x
rm "$OUTPUT_FILE"

pushd $PYDBN_BASE

zip -r $OUTPUT_FILE \
  evm_compiler/ \
  parser/  \
  evm_compile_lambda.py \
  -x \*.pyc -x __pycache__

popd
