

// Uses window.hostname to determine environment

const devAddress = [
	'0x64486715303218136817354C3350f741Bb592c98',
]

const configForEnvironment = {
	localhost: {
		compileEndpoint: '/evm_compile',
		coordinatorContractAddress: process.env.REACT_APP_DBN_COORDINATOR_CONTRACT_ADDRESS_DEVELOPMENT,
		ethNetwork: 'http://localhost:8545',
		verbose: true,
		mintWhitelist: devAddress,

		useHelpers: true,
		helperAddress: '0x19af9857f53675c17248113E2818eaBBEb8089DE',
	},

	localhost_rinkeby: {
		compileEndpoint: '/evm_compile',
		coordinatorContractAddress: process.env.REACT_APP_DBN_COORDINATOR_CONTRACT_ADDRESS_RINKEBY,
		ethNetwork: 'https://eth-rinkeby.alchemyapi.io/v2/qR_K_URkIpNbjY0HlvWACZIao-tEdX94',
		verbose: true,
		testnetBanner: true,
		mintWhitelist: devAddress,
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
		coordinatorContractAddress: "0xC6730c7cDd99e8c38B0bc73Da99C188985DF0b39",
		ethNetwork: 'https://eth-rinkeby.alchemyapi.io/v2/qR_K_URkIpNbjY0HlvWACZIao-tEdX94',
		testnetBanner: true,
		mintWhitelist: devAddress,
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