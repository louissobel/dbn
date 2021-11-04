
artifacts/intermediate_ethasm/singleContractDrawHarness.ethasm : \
	contracts/RenderDBN/drawHarness.ethasm \
	contracts/RenderDBN/initializeBitmap.ethasm \
	contracts/RenderDBN/lineCommand.ethasm \
	contracts/RenderDBN/setCommand.ethasm \
	contracts/RenderDBN/paperCommand.ethasm \
	contracts/RenderDBN/clampValue.ethasm \
	contracts/RenderDBN/envGet.ethasm \
	contracts/RenderDBN/dotGet.ethasm
	cat $^ > $@

.PRECIOUS : artifacts/drawings/%.ethasm
artifacts/drawings/%.ethasm : \
	artifacts/intermediate_ethasm/singleContractDrawHarness.ethasm \
	artifacts/intermediate_ethasm/drawings/%.ethasm
	cat $^ > $@


app/src/contracts/drawHarness.ethasm : artifacts/intermediate_ethasm/singleContractDrawHarness.ethasm
	cp $^ $@

app/src/contracts/DBNCoordinator.json : artifacts/contracts/DBNCoordinator.sol/DBNCoordinator.json
	cp $^ $@

artifacts/contracts/DBNCoordinator.sol/DBNCoordinator.json: FORCE
	hh compile
FORCE:


.PHONY : frontend
frontend: \
	app/src/contracts/drawHarness.ethasm \
	app/src/contracts/DBNCoordinator.json

artifacts/intermediate_ethasm/drawings/scratch_drawings/%.ethasm : scratch_drawings/%.dbn $(wildcard ../pydbn/**/*)
	python ../pydbn/dbn.py $< --evm \
		--evm-owning-contract 0xAABBCCDDEEFFAABBCCDDEEFFAABBCCDDEEFF1234 \
		--evm-description 0x736372617463685f64726177696e67 \
		> $@

# Unit tests

artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm : \
	contracts/RenderDBN/testHarness.ethasm \
	contracts/RenderDBN/initializeBitmap.ethasm \
	contracts/RenderDBN/base64encode.ethasm \
	contracts/RenderDBN/setCommand.ethasm \
	contracts/RenderDBN/lineCommand.ethasm \
	contracts/RenderDBN/paperCommand.ethasm \
	contracts/RenderDBN/clampValue.ethasm
	cat $^ > artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm

artifacts/contracts/RenderDBNTestArtifact.eth : artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm
	hh assemble --file $^ --output $@

testHarness : artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm

artifacts/contracts/drawings/%.eth : artifacts/drawings/%.ethasm
	hh assemble --file $^ --output $@

.PHONY : testbase64
testbase64 : artifacts/contracts/RenderDBNTestArtifact.eth
	hh test ./test/draw-base64encode-test.js

.PHONY : testInitializeBitmap
testInitializeBitmap : artifacts/contracts/RenderDBNTestArtifact.eth
	hh test ./test/draw-initializeBitmap-test.js

.PHONY : testLineCommand
testLineCommand : artifacts/contracts/RenderDBNTestArtifact.eth
	hh test ./test/draw-lineCommand-test.js

.PHONY : testPaperCommand
testPaperCommand : artifacts/contracts/RenderDBNTestArtifact.eth
	hh test ./test/draw-paperCommand-test.js

.PHONY : unitTest
unitTest : testbase64 testInitializeBitmap testLineCommand testPaperCommand

# Drawing Tests
test/drawings/%/actual.bmp: artifacts/drawings/test/%.ethasm
	hh assemble-and-run --file $< --output-file $@

artifacts/intermediate_ethasm/drawings/test/%.ethasm : test/drawings/%/input.dbn $(wildcard ../pydbn/**/*)
	python ../pydbn/dbn.py $< --evm > $@

TEST ?= *
.PHONY : drawingTest
drawingTest : $(foreach f, $(wildcard test/drawings/${TEST}), $f/actual.bmp)
	./scripts/drawing-test.sh $^

.PHONY : test
test : drawingTest unitTest


.PHONY : clean
clean:
	rm -f artifacts/intermediate_ethasm/*.ethasm
	rm -f artifacts/intermediate_ethasm/drawings/test/*.ethasm

	rm -f artifacts/drawings/*.ethasm
	rm -f artifacts/drawings/test/*.ethasm


.DELETE_ON_ERROR:
