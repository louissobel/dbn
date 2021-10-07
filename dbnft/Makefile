
artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm : \
	contracts/RenderDBN/testHarness.ethasm \
	contracts/RenderDBN/initializeBitmap.ethasm \
	contracts/RenderDBN/base64encode.ethasm
	cat $^ > artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm

artifacts/contracts/RenderDBNTestArtifact.eth : artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm
	hh assemble --file artifacts/intermediate_ethasm/RenderDBNTestArtifact.ethasm --output artifacts/contracts/RenderDBNTestArtifact.eth

.PHONY : testbase64
testbase64 : artifacts/contracts/RenderDBNTestArtifact.eth
	hh test ./test/draw-base64encode-test.js

.PHONY : testInitializeBitmap
testInitializeBitmap : artifacts/contracts/Draw.eth
	hh test ./test/draw-initializeBitmap-test.js


.PHONY : testRenderDBN
testRenderDBN : testbase64 testInitializeBitmap
