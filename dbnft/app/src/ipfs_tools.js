import { create } from 'ipfs-http-client'

import frontendEnvironment from './frontend_environment'


async function getTextFileFromGateway(cid) {
  const url = frontendEnvironment.config.ipfsGateway + cid;
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error('fetch to ' + url + ' failed: ' + response.status)
  }
  return await response.text()
}

async function pinFileToPinata(code) {
  const url = frontendEnvironment.config.pinataBase + 'pinning/pinFileToIPFS';
  const pinataJWT = frontendEnvironment.config.pinataJWT;

  const data = new FormData()
  data.append('file', new Blob([code]))

  const pinataOptions = JSON.stringify({
    cidVersion: 0,
  });
  data.append('pinataOptions', pinataOptions);

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${pinataJWT}`
    },
    body: data,
  })

  if (!response.ok) {
    throw new Error('non-200 from pinata API: ', response.status)
  }

  return (await response.json()).IpfsHash
}



const localIPFSClient = {
	getTextFile: getTextFileFromGateway,

  async pinFile(code) {
    const client = create('http://localhost:5001');
    const result = await client.add(code)
    return result.cid.toString()
  }
}

const pinataIPFSClient = {
  getTextFile: getTextFileFromGateway,
  pinFile: pinFileToPinata,
}


function getClient() {
  switch (frontendEnvironment.config.ipfsClient) {
    case 'local':
      return localIPFSClient;
    case 'pinata':
      return pinataIPFSClient
    default:
      throw new Error('cannot select ipfs client: ' +  frontendEnvironment.config.ipfsClient)
  }
}

export const ipfsClient = getClient();
