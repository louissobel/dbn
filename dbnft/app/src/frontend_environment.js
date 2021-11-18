

// Uses window.hostname to determine environment

const configForEnvironment = {
	localhost: {
		compileEndpoint: '/evm_compile',
		coordinatorContractAddress: '0xB80451635D64585424bd18daCC9116DadD77d44D',
		expectedChainId: 1337,
		mintPrice: 10000000000000000, // 0.01 ETH
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
	},

	localhost_rinkeby: {
		coordinatorContractAddress: '0xc3D8F3cFE4628feBa2208fB1CE2d479a3A81037f',
		ethNetwork: 'https://eth-rinkeby.alchemyapi.io/v2/qR_K_URkIpNbjY0HlvWACZIao-tEdX94',
		testnetBanner: true,
		helperAddress: '0x5AA6e8F2962AB0A9B99f52F366eACaA8382721f5',

		compileEndpoint: '/evm_compile',
		expectedChainId: 4,
		mintPrice: 10000000000000000, // 0.01 ETH
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
		coordinatorContractAddress: "0xb9566c09b4CE32E9297f8A2601FB30ea58EcDeb3",
		expectedChainId: 4,
		mintPrice: 10000000000000000, // 0.01 ETH
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