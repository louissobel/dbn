


async function main() {
	const params = [
		  {
		    name: null,
		    type: 'string',
		    indexed: null,
		    components: null,
		    arrayLength: null,
		    arrayChildren: null,
		    baseType: 'string',
		    _isParamType: true
		  }
		]

			     "0x0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000568656c6c6f000000000000000000000000000000000000000000000000000000"
	const data = "0x0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000568656c6c6f000000000000000000000000000000000000000000000000000000"

	const c = new ethers.utils.AbiCoder()
	console.log(c.encode(params, ["hello"]))

	console.log(c.decode(params, data))
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });





/*
[
  ParamType {
    name: null,
    type: 'string',
    indexed: null,
    components: null,
    arrayLength: null,
    arrayChildren: null,
    baseType: 'string',
    _isParamType: true
  }
]
Uint8Array(96) [
  0, 0, 0, 0,   0,   0,   0,   0,   0, 0, 0, 0,
  0, 0, 0, 0,   0,   0,   0,   0,   0, 0, 0, 0,
  0, 0, 0, 0,   0,   0,   0,   1,   0, 0, 0, 0,
  0, 0, 0, 0,   0,   0,   0,   0,   0, 0, 0, 0,
  0, 0, 0, 0,   0,   0,   0,   0,   0, 0, 0, 0,
  0, 0, 0, 5, 104, 101, 108, 108, 111, 0, 0, 0,
  0, 0, 0, 0,   0,   0,   0,   0,   0, 0, 0, 0,
  0, 0, 0, 0,   0,   0,   0,   0,   0, 0, 0, 0
]
*/