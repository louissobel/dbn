

.PRECIOUS : artifacts/intermediate_ethasm/drawings/%.ethasm
artifacts/intermediate_ethasm/drawings/%.ethasm : drawings/%.dbn $(wildcard ../pydbn/**/*)
	python ../pydbn/dbn.py $< --evm > $@

artifacts/drawings/%.ethasm : \
	contracts/RenderDBN/drawHarness.ethasm \
	artifacts/intermediate_ethasm/drawings/%.ethasm \
	contracts/RenderDBN/initializeBitmap.ethasm \
	contracts/RenderDBN/lineCommand.ethasm \
	contracts/RenderDBN/setCommand.ethasm \
	contracts/RenderDBN/paperCommand.ethasm \
	contracts/RenderDBN/clipColor.ethasm
	cat $^ > $@

artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm : \
	contracts/RenderDBN/testHarness.ethasm \
	contracts/RenderDBN/initializeBitmap.ethasm \
	contracts/RenderDBN/base64encode.ethasm \
	contracts/RenderDBN/lineCommand.ethasm \
	contracts/RenderDBN/paperCommand.ethasm \
	contracts/RenderDBN/clipColor.ethasm
	cat $^ > artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm

testHarness : artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm

artifacts/contracts/RenderDBNTestArtifact.eth : artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm
	hh assemble --file artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm --output artifacts/contracts/RenderDBNTestArtifact.eth

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

.PHONY : test
test : testbase64 testInitializeBitmap testLineCommand testPaperCommand

