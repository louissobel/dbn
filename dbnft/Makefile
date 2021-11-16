
artifacts/intermediate_ethasm/helpers.ethasm : \
	contracts/RenderDBN/helpers/helpersHarness.ethasm \
	$(wildcard contracts/RenderDBN/helpers/impl/*) \
	contracts/RenderDBN/inlined/clampValue.ethasm
	cat $^ > $@

artifacts/contracts/helpers.eth : artifacts/intermediate_ethasm/helpers.ethasm
	hh assemble --file $^ --output $@

artifacts/intermediate_ethasm/helpersLinkArtifact.json : \
	$(wildcard contracts/RenderDBN/helpers/remoteClient/*) \
	$(wildcard contracts/RenderDBN/inlined/*)
	python scripts/make_link_artifact.py $^ --output $@

artifacts/intermediate_ethasm/inlineLinkArtifact.json : \
	$(wildcard contracts/RenderDBN/helpers/inlineClient/*) \
	$(wildcard contracts/RenderDBN/helpers/impl/*) \
	$(wildcard contracts/RenderDBN/inlined/*)
	python scripts/make_link_artifact.py $^ --output $@

.PRECIOUS : artifacts/drawings/%.helpers.ethasm
artifacts/drawings/%.helpers.ethasm: \
	artifacts/intermediate_ethasm/drawings/%.helpers.ethasm \
	contracts/RenderDBN/drawHarness.ethasm \
	artifacts/intermediate_ethasm/helpersLinkArtifact.json
	python scripts/link.py \
		--drawing $< \
		--harness contracts/RenderDBN/drawHarness.ethasm \
		--functions artifacts/intermediate_ethasm/helpersLinkArtifact.json \
		--output $@

.PRECIOUS : artifacts/drawings/%.ethasm
artifacts/drawings/%.ethasm : \
	artifacts/intermediate_ethasm/drawings/%.ethasm \
	contracts/RenderDBN/drawHarness.ethasm \
	artifacts/intermediate_ethasm/inlineLinkArtifact.json
	python scripts/link.py \
		--drawing $< \
		--harness contracts/RenderDBN/drawHarness.ethasm \
		--functions artifacts/intermediate_ethasm/inlineLinkArtifact.json \
		--output $@

app/src/contracts/drawHarness.ethasm : contracts/RenderDBN/drawHarness.ethasm
	cp $^ $@

app/src/contracts/inlineLinkArtifact.json : artifacts/intermediate_ethasm/inlineLinkArtifact.json
	cp $^ $@

app/src/contracts/helpersLinkArtifact.json : artifacts/intermediate_ethasm/helpersLinkArtifact.json
	cp $^ $@

app/src/contracts/DBNCoordinator.json : artifacts/contracts/DBNCoordinator.sol/DBNCoordinator.json
	jq .abi $^ > $@

artifacts/contracts/DBNCoordinator.sol/DBNCoordinator.json: FORCE
	hh compile
FORCE:


.PHONY : frontend
frontend: \
	app/src/contracts/drawHarness.ethasm \
	app/src/contracts/inlineLinkArtifact.json \
	app/src/contracts/helpersLinkArtifact.json \
	app/src/contracts/DBNCoordinator.json

artifacts/intermediate_ethasm/drawings/scratch_drawings/%.ethasm : scratch_drawings/%.dbn $(wildcard ../pydbn/**/*)
	python ../pydbn/dbn.py $< --evm \
		--evm-description 0x736372617463685f64726177696e67 \
		> $@

# Unit tests

artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm : \
	contracts/RenderDBN/testHarness.ethasm \
	contracts/RenderDBN/helpers/impl/initializeBitmapImpl.ethasm \
	contracts/RenderDBN/base64encode.ethasm \
	contracts/RenderDBN/inlined/setCommand.ethasm \
	contracts/RenderDBN/inlined/lineCommand.ethasm \
	contracts/RenderDBN/helpers/impl/linePixelsImpl.ethasm \
	contracts/RenderDBN/helpers/impl/paperCommandImpl.ethasm \
	contracts/RenderDBN/inlined/clampValue.ethasm
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
	hh assemble-and-run --file $< --output-file $@ --fixed-timestamp 1636140613

test/drawings/%/actual.helpers.bmp: \
	artifacts/drawings/test/%.helpers.ethasm \
	artifacts/contracts/helpers.eth
	hh assemble-and-run --file $< --output-file $@ --fixed-timestamp 1636140613\
		--load-contract 0xAABBCCDDEEFFAABBCCDDEEFFAABBCCDDEEFF1234:artifacts/contracts/helpers.eth

artifacts/intermediate_ethasm/drawings/test/%.ethasm : test/drawings/%/input.dbn $(wildcard ../pydbn/**/*)
	python ../pydbn/dbn.py $< --evm > $@

artifacts/intermediate_ethasm/drawings/test/%.helpers.ethasm : test/drawings/%/input.dbn $(wildcard ../pydbn/**/*)
	python ../pydbn/dbn.py $< --evm --evm-helper-address 0xAABBCCDDEEFFAABBCCDDEEFFAABBCCDDEEFF1234 > $@

TEST ?= *
.PHONY : drawingTestInline
drawingTestInline : $(foreach f, $(wildcard test/drawings/${TEST}), $f/actual.bmp)
	./scripts/drawing-test.sh $^

.PHONY : drawingTestHelpers
drawingTestHelpers : $(foreach f, $(wildcard test/drawings/${TEST}), $f/actual.helpers.bmp)
	./scripts/drawing-test.sh $^

.PHONY : drawingTest
drawingTest: drawingTestInline drawingTestHelpers

.PHONY : test
test : drawingTest unitTest


.PHONY : clean
clean:
	rm -f artifacts/intermediate_ethasm/*.ethasm
	rm -f artifacts/intermediate_ethasm/drawings/test/*.ethasm

	rm -f artifacts/drawings/*.ethasm
	rm -f artifacts/drawings/test/*.ethasm


.DELETE_ON_ERROR:
