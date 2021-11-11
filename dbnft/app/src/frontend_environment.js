

// Uses window.hostname to determine environment

const devAddress = [
	'0x64486715303218136817354C3350f741Bb592c98',
]

const configForEnvironment = {
	localhost: {
		compileEndpoint: '/evm_compile',
		coordinatorContractAddress: '0xFB04D45B68ce4d18324D228B1Ed8829C792Acb97',
		mintPrice: 10000000000000000, // 0.01 ETH
		ethNetwork: 'http://localhost:8545',
		verbose: true,

		useHelpers: true,
		helperAddress: '0x19af9857f53675c17248113E2818eaBBEb8089DE',

		openSeaBase: 'https://testnets.opensea.io',
		etherscanBase: 'https://rinkeby.etherscan.io',
	},

	localhost_rinkeby: {
		compileEndpoint: '/evm_compile',
		coordinatorContractAddress: process.env.REACT_APP_DBN_COORDINATOR_CONTRACT_ADDRESS_RINKEBY,
		ethNetwork: 'https://eth-rinkeby.alchemyapi.io/v2/qR_K_URkIpNbjY0HlvWACZIao-tEdX94',
		verbose: true,
		testnetBanner: true,
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
		coordinatorContractAddress: "0xF58eCE1a86A64B12CecAeb0A8EcfF600B8158e5f",
		mintPrice: 10000000000000000, // 0.01 ETH
		ethNetwork: 'https://eth-rinkeby.alchemyapi.io/v2/qR_K_URkIpNbjY0HlvWACZIao-tEdX94',
		testnetBanner: true,

		useHelpers: true,
		helperAddress: '0x5AA6e8F2962AB0A9B99f52F366eACaA8382721f5',

		openSeaBase: 'https://testnets.opensea.io',
		etherscanBase: 'https://rinkeby.etherscan.io',
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