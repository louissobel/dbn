
artifacts/contracts/Draw.eth : contracts/Draw.ethasm
	hh assemble --file contracts/Draw.ethasm --output artifacts/contracts/Draw.eth 

.PHONY : testbase64
testbase64 : artifacts/contracts/Draw.eth
	hh test ./test/draw-base64encode-test.js
