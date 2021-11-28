// utility library for interacting with allowlist
// / and the cryptographic tickets

import frontendEnvironment from './frontend_environment'
import {dbnCoordinator} from './eth_tools'


class Ticket {
  // format:
  // DBNFT:tokenId:minter:coordinator:ticketId:signature
  static fromString(s) {
    const parts = s.split(':')
    if (parts.length !== 6) {
      throw new Error("invalid format: should be 6 parts separated by a :")
    }

    // should we do... more validation?
    // or just expect that callers will call verify.
    return new Ticket({
      tokenId: parts[1],
      minter: parts[2],
      coordinator: parts[3],
      ticketId: parts[4],
      signature: parts[5],
    })
  }

  serialize() {
    const parts = [
      "DBNFT",
      this.tokenId,
      this.minter,
      this.coordinator,
      this.ticketId,
      this.signature
    ]
    return parts.join(":")
  }

  static async generate(web3, signer, opts) {
    const data = this.signingData(web3, opts)
    let signature = await web3.eth.personal.sign(data, signer)

    // work around ledger passing bad v...
    let everythingExceptLastByte = signature.slice(0, signature.length - 2)
    let lastByte = signature.slice(signature.length - 2, signature.length)

    // if it's zero or one add 27
    if (lastByte === '00') {
      lastByte = '1b'
    } else if (lastByte === '01') {
      lastByte = '1c'
    }
    signature = everythingExceptLastByte + lastByte;

    return new Ticket({
      tokenId: opts.tokenId,
      minter: opts.minter,
      coordinator: opts.coordinator,
      ticketId: opts.ticketId,
      signature: signature
    })
  }

  constructor(opts) {
    this.tokenId = opts.tokenId;
    this.minter = opts.minter;
    this.coordinator = opts.coordinator;
    this.ticketId = opts.ticketId;
    this.signature = opts.signature;
  }

  async verify(web3, opts) {
    const data = Ticket.signingData(web3, this)
    const signer = await web3.eth.personal.ecRecover(
      data,
      this.signature,
    )

    if (web3.utils.toChecksumAddress(signer) !== opts.signer) {
      throw new Error(`Invalid signature (got signer ${signer})`)
    }    

    if (this.coordinator !== opts.coordinator) {
      throw new Error(`Ticket for a different coordinator configured:${opts.coordinator} signed:${this.coordinator}`)
    }

    if (this.minter !== opts.minter) {
      throw new Error(`Ticket for a different minter configured:${opts.minter} signed:${this.minter}`)
    }
  }

  static signingData(web3, data) {
    const params = web3.eth.abi.encodeParameters(
      ['address', 'address', 'uint256', 'uint256'],
      [
        data.coordinator,
        data.minter,
        data.tokenId,
        data.ticketId
      ],
    );
    return web3.utils.keccak256(params)
  }
}


class Allowlist {
  static FINISHED = frontendEnvironment.config.allowlistFinished;

  // TODO: get this somewhere more easily configurable
  static _allowlistHints = {
    '0': '0xD48DB54EAFD7D529865ACa71419506eC5fbeD4AB',
  }

  // Note: this is _just a hint_ for the frontend to provide better user-experience
  // The actual validation occurs via the "ticket", a signed tuple of
  // the minter, the coordinator, a ticketId, and the token id
  static async getMintableTokenIds(account) {
    const alreadyMinted = await dbnCoordinator.methods.mintedAllowlistedTokens().call()

    let allowed = []
    for (let e of Object.entries(this._allowlistHints)) {
      if (e[1] === account && !alreadyMinted.includes(e[0])) {
        allowed.push(e[0])
      }
    }
    return allowed;
  }
}

export {Ticket}
export default Allowlist