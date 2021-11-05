

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

for actual in $@
do
	folder=$(dirname $actual)
	compareOutput=$(compare -metric AE \
		$actual \
		$folder/expected.bmp \
		$folder/diff.png 2>&1
	)

	if [ $? -ne 0 ]; then
		printf "$folder: ${RED}FAIL: Images dont match!${NC}: Diff at $folder/diff.png\n"
		printf "compare output:\n$compareOutput\n"
	else
		printf "$folder: ${GREEN}OK!${NC}\n"
	fi

done