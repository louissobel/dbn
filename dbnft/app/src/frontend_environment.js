

// Uses window.hostname to determine environment

const configForEnvironment = {
	localhost: {
		compileEndpoint: '/evm_compile',
		coordinatorContractAddress: '0x42e4d2525C8a83a30367fba8412874f37bfCc0EC',

		// we _could_ look this up, but simplifies things to hardcode
		coordinatorOwner: '0x64486715303218136817354C3350f741Bb592c98',
		expectedChainId: 1337,
		ethNetwork: 'http://localhost:8545',
		verbose: true,

		useHelpers: true,
		helperAddress: '0x19af9857f53675c17248113E2818eaBBEb8089DE',
		interpreterChainId: 4,

		externalBase: 'http://localhost:3000/dbnft/',
		openSeaBase: 'https://testnets.opensea.io',
		etherscanBase: 'https://rinkeby.etherscan.io',

		ipfsGateway: 'http://localhost:8080/ipfs/',
		ipfsClient: 'local',

		allowlistHintURL: 'https://dbnft.s3.amazonaws.com/localhost/allowlist_hints.json',
	},

	localhost_rinkeby: {
		coordinatorContractAddress: '0xc3D8F3cFE4628feBa2208fB1CE2d479a3A81037f',
		ethNetwork: 'https://eth-rinkeby.alchemyapi.io/v2/qR_K_URkIpNbjY0HlvWACZIao-tEdX94',
		testnetBanner: true,
		helperAddress: '0x5AA6e8F2962AB0A9B99f52F366eACaA8382721f5',

		compileEndpoint: '/evm_compile',
		expectedChainId: 4,
		verbose: true,

		useHelpers: true,
		interpreterChainId: 4,

		externalBase: 'http://localhost:3000/dbnft/',
		openSeaBase: 'https://testnets.opensea.io',
		etherscanBase: 'https://rinkeby.etherscan.io',

		ipfsGateway: 'http://localhost:8080/ipfs/',
		ipfsClient: 'local',
	},

	// should this be testnet?
	cloudflareStaging: {
		compileEndpoint: 'https://1ard2p8bka.execute-api.us-east-1.amazonaws.com/preview/evm_compile',
		coordinatorContractAddress: "0x1B11e128180603A62f28c9D60B1DcdaD8B5D8a16",
		ethNetwork: 'http://localhost:8545',
		verbose: true,
	},

	testnet: {
		compileEndpoint: 'https://1ard2p8bka.execute-api.us-east-1.amazonaws.com/evm_compile',
		coordinatorContractAddress: "0xAE4AB04EF112AF11A726Ee87b08C781084a17eE9",
		coordinatorOwner: '0x64486715303218136817354C3350f741Bb592c98',
		expectedChainId: 4,
		ethNetwork: 'https://eth-rinkeby.alchemyapi.io/v2/qR_K_URkIpNbjY0HlvWACZIao-tEdX94',
		testnetBanner: true,

		useHelpers: true,
		helperAddress: '0x5AA6e8F2962AB0A9B99f52F366eACaA8382721f5',
		interpreterChainId: 4,

		externalBase: 'https://testnet.dbnft.io/dbnft/',
		openSeaBase: 'https://testnets.opensea.io',
		etherscanBase: 'https://rinkeby.etherscan.io',

		ipfsGateway: 'https://cloudflare-ipfs.com/ipfs/',
		pinataBase: 'https://api.pinata.cloud/',
		pinataJWT: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI1NzY4MmRiYy1kZWQ3LTQzOTEtODFjOC05NGYyNWY3NGI3MzEiLCJlbWFpbCI6ImxvdWlzLmEuc29iZWxAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siaWQiOiJOWUMxIiwiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjF9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZX0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjQxYmI4OTY0NGRiOTQ0NWRhZTI1Iiwic2NvcGVkS2V5U2VjcmV0IjoiMzJiZjk1MDhhZTc0Y2I0MTkxMTYzNjlkNWQ0OTM4NDA2N2Y3YzU4NGZhMjUyM2Q5N2VjMDllM2IyZmJiM2Q4ZSIsImlhdCI6MTYzNjc0MzA0MH0.DPp_EznnjBQFkluj08HLJulV19amqm1Ft4NSua6Hy2I',
		ipfsClient: 'pinata',

		allowlistHintURL: 'https://dbnft.s3.amazonaws.com/testnet/allowlist_hints.json',
	},

	mainnet: {
		compileEndpoint: 'https://1ard2p8bka.execute-api.us-east-1.amazonaws.com/evm_compile',
		coordinatorContractAddress: "0x8922A71214BACa269Ac7cdB455e8570fB75235Ca",
		coordinatorOwner: '0xD48DB54EAFD7D529865ACa71419506eC5fbeD4AB',
		expectedChainId: 1,
		ethNetwork: 'https://eth-mainnet.alchemyapi.io/v2/_4223fENskrfn54r3E5OVS1c6E5FXSYA',

		useHelpers: true,
		helperAddress: '0x31b3D54e7Ef57709ef809e5749E9840cd9BC45Cc',
		interpreterChainId: 1,

		externalBase: 'https://dbnft.io/dbnft/',
		openSeaBase: 'https://opensea.io',
		etherscanBase: 'https://etherscan.io',

		ipfsGateway: 'https://cloudflare-ipfs.com/ipfs/',
		pinataBase: 'https://api.pinata.cloud/',
		pinataJWT: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI1NzY4MmRiYy1kZWQ3LTQzOTEtODFjOC05NGYyNWY3NGI3MzEiLCJlbWFpbCI6ImxvdWlzLmEuc29iZWxAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siaWQiOiJOWUMxIiwiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjF9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZX0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjQxYmI4OTY0NGRiOTQ0NWRhZTI1Iiwic2NvcGVkS2V5U2VjcmV0IjoiMzJiZjk1MDhhZTc0Y2I0MTkxMTYzNjlkNWQ0OTM4NDA2N2Y3YzU4NGZhMjUyM2Q5N2VjMDllM2IyZmJiM2Q4ZSIsImlhdCI6MTYzNjc0MzA0MH0.DPp_EznnjBQFkluj08HLJulV19amqm1Ft4NSua6Hy2I',
		ipfsClient: 'pinata',

		allowlistHintURL: 'https://dbnft.s3.amazonaws.com/mainnet/allowlist_hints.json',
	},
}

const UNKNOWN_CONFIG = {environment: 'unknown'}

const environmentFromHostname = function (hostname) {
	if (hostname === 'localhost') {
		if (process.env.REACT_APP_LOCALHOST_USE_RINKEBY === 'true') {
			return 'localhost_rinkeby'
		}
		return 'localhost'
	} else if (hostname.match(/.+?\.dbnft\.pages\.dev/)) {
		return 'cloudflareStaging'
	} else if (hostname === 'testnet.dbnft.io') {
		return 'testnet'
	} else if (hostname === 'dbnft.io') {
		return 'mainnet'
	} else {
		return null
	}
}

const config = function() {
	if (!window.location) {
		console.warn('cannot determine frontend environemnt without window. is this within a webworker')
		return UNKNOWN_CONFIG
	}

	const environment = environmentFromHostname(window.location.hostname)
	if (!environment) {
		console.warn('unable to detect environment, hostname: ', window.location.hostname)
		return UNKNOWN_CONFIG
	}

	if (!configForEnvironment[environment]) {
		console.warn('no config defined for environment ' + environment)
		return UNKNOWN_CONFIG
	}

	const config = {
		environment: environment,
		config: configForEnvironment[environment]
	}
	console.log(config)
	return config
}






const frontendEnvironment = config()


export default frontendEnvironment;