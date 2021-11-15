import './dbn_renderer_worker_etherjs_workaround'
import {evmAssemble, evmInterpret, linkCode} from './evm_tools'
import helperContractCodeByAddress from './helper_contracts'
import { BN } from 'ethereumjs-util'

const GAS_LIMIT = new BN(0xffffffff)

const MASK_160 = new BN(1).shln(160).subn(1)

onmessage = ({ data }) => {
  var renderFn;
  if (data.code || data.code === "") {
    renderFn = renderDBN;
  } else if (data.bytecode) {
    renderFn = renderDBNFromBytecode
  } else {
    throw new Error("unhandled request: " + data)
  }

  const opts = {
    compileEndpoint: data.frontendEnvironment.config.compileEndpoint,
    verbose: data.frontendEnvironment.config.verbose,

    codeAddress: data.codeAddress,

    useHelpers: data.useHelpers,
    helperAddress: data.helperAddress,

    chainId: data.frontendEnvironment.config.interpreterChainId,
  }

  if (opts.useHelpers && !opts.helperAddress) {
    throw new Error("useHelpers set but no helperAddress provided")
  }

  try {
    renderFn(data, opts, (s, d) => {
      postMessage({
        message: 'update',
        value: {
          update: s,
          data: d,
        }
      })
    })
    .then((result) => {
      if (result.error) {
        postMessage({
          message: 'error',
          value: result.error,
        })
      } else {
        postMessage({
          message: 'result',
          value: result,
        })
      }
    })
    .catch((error) =>
      postMessage({
        message: 'error',
        value: error
      })
    )
  } catch (error) {
    postMessage({
      message: 'error',
      value: error
    })
  }
};

const maybeReportStaticcall = function(step, opts) {
  if (step.stack.length < 2) {
    // let the EVM throw the underflow...
    return
  }
  let addressStackSlot = step.stack[step.stack.length - 2];
  let address = addressStackSlot.and(MASK_160).toString(16)
  if (address !== opts.helperAddress) {
    postMessage({
      message: 'blockchain_data_needed',
      value: {
        opcode: step.opcode.name,
        address: address,
      }
    })
  }
}

const maybeReportBalance = function(step) {
  if (step.stack.length < 1) {
    // let the EVM throw the underflow...
    return
  }
  let addressStackSlot = step.stack[step.stack.length - 1];
  let address = addressStackSlot.and(MASK_160).toString(16)
  // A balance call to _any_ address traps to the blockchain
  postMessage({
    message: 'blockchain_data_needed',
    value: {
      opcode: step.opcode.name,
      address: address,
    }
  })
}

const maybeReportLog1 = function(step) {
  if (step.stack.length < 3) {
    // let the EVM throw the underflow...
    return
  }

  // stack is [data|dataLength|topic0
  // (where topic0 is line no and we _assume_
  // that data is always 32 bytes at 0x80 😁)
  let lineNo = step.stack[step.stack.length - 3].toNumber()
  let value = new BN(step.memory.slice(0x80, 0x80 + 32), 'be')

  postMessage({
    message: 'update',
    value: {
      update: 'LOG',
      data: {
        lineNo: lineNo,
        value: value.toString(16, 2),
      }
    }
  }) 
}

const makeStepListener = function(throttleInterval, opts) {
  var lastCalled = 0;
  return function(step) {
    // Report calls / balance to identify when the drawing
    // is trying to access actual blockchain data.
    if (step.opcode.name === 'STATICCALL') {
      maybeReportStaticcall(step, opts)
    }

    if (step.opcode.name === 'BALANCE') {
      maybeReportBalance(step)
    }

    // Report Logs as they happen (only is log1 supported)
    if (step.opcode.name === 'LOG1') {
      maybeReportLog1(step)
    }

    const now = Date.now();
    if (now - lastCalled > throttleInterval) {

      // We KNOW the Bitmap lives at 0x0180....
      // And that it's 10962 long...
      //
      // We also know that 0x0B in memory is used
      // as flag that the "bitmap is ready"
      var wipImage = null;
      if (step.memory[0x0B]) {

        // Create a bitmap. We can't just return step.memory.slice
        // because we lazily allocate the bitmap memory in the EVM,
        // so there might not be a whole valid bitmap!
        const bitmapLength = 10962;
        const wipBitmapData = new Uint8Array(bitmapLength)
        wipBitmapData.set(step.memory.subarray(0x0180, 0x0180 + 10962))

        wipImage = new Blob(
          [wipBitmapData],
          {type: 'image/bmp'}
        )

        postMessage({
          message: 'update',
          value: {
            update: 'INTERPRET_PROGRESS',
            data: {
              imageData: wipImage,
              gasUsed: (GAS_LIMIT - step.gasLeft).toString()
            }
          }
        })

        lastCalled = now;
      }
    }
  }
}

const renderDBN = async function(data, opts, onRenderStateChange) {
  onRenderStateChange('COMPILE_START', {})

  const metadata = {};
  if (opts.helperAddress) {
    metadata['helper_address'] = opts.helperAddress
  }
  if (data.description) {
    metadata['description'] = "0x" + Buffer.from(data.description, 'utf-8').toString('hex')
  }

  const response = await fetch(opts.compileEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      code: data.code,
      metadata: metadata,
    }),
  })
  if (!response.ok) {
    throw new Error('Unexpected result: ' + response.status);
  }
  const responseData = await response.json()
  if (responseData.error) {
    return {
      error: {
        type: responseData.error.type,
        message: responseData.error.message,
        lineNumber: responseData.error.line_number,
        relatedLineNumber: responseData.error.related_line_number,
        lineNumberInMessage: responseData.error.line_number_in_message,
      }
    }
  }

  const assemblyCode = responseData.result;

  if (opts.verbose) {
    console.log(assemblyCode)
  }
  onRenderStateChange('COMPILE_END', {result: assemblyCode})


  onRenderStateChange('LINK_START', {})
  const linkedAssembly = linkCode(assemblyCode, {
    useHelpers: opts.useHelpers,
  })
  if (opts.verbose) {
    console.log(linkedAssembly)
  }
  onRenderStateChange('LINK_END', {result: linkedAssembly})

  onRenderStateChange('ASSEMBLE_START', {})
  const bytecode = await evmAssemble(linkedAssembly)
  if (opts.verbose) {
    console.log(bytecode)
  }
  onRenderStateChange('ASSEMBLE_END', {result: bytecode})

  const interpretResult = await renderDBNFromBytecode({bytecode: bytecode}, opts, onRenderStateChange)

  var renderedDescription;
  if (data.description) {
    // then pull it back out of the bytecode :)

    onRenderStateChange('GET_DESCRIPTION_START', {})
    const descriptionResult = await evmInterpret(
      bytecode,
      {
        gasLimit: GAS_LIMIT,
        data: Buffer.from([0xDE]),
        chainId: opts.chainId,
      },
    )
    onRenderStateChange('GET_DESCRIPTION_END', {})

    if (descriptionResult.exceptionError) {
      throw new Error(descriptionResult.exceptionError.error)
    }

    renderedDescription = Buffer.from(descriptionResult.returnValue).toString('utf-8')
    if (renderedDescription !== data.description) {
      throw new Error("description did not roundtrip!")
    }
  }

  return {
    imageData: interpretResult.imageData,
    gasUsed: interpretResult.gasUsed,
    renderedDescription: renderedDescription,
  }
}

const renderDBNFromBytecode = async function(data, opts, onRenderStateChange) {
  onRenderStateChange('INTERPRET_START', {})

  // First, attempt to get a "helper address" to load in
  const helperAddressResult = await evmInterpret(
    data.bytecode,
    {
      gasLimit: GAS_LIMIT,
      data: Buffer.from([0x33]),
      chainId: opts.chainId,
    }
  )
  let helperAddress = Buffer.from(helperAddressResult.returnValue).toString('hex');
  if (helperAddressResult.exceptionError) {
    if (helperAddressResult.exceptionError.error === 'revert') {
      console.warn('revert getting helperaddress: ' + helperAddress)
      helperAddress = ""
    } else {
      throw new Error('error getting helper address: ' + helperAddress.exceptionError.error)
    }
  }

  let helper = null;
  if (helperAddress) {
    if (opts.verbose) {
      console.log("using helpers from address " + helperAddress)
    }
    const helperCode = helperContractCodeByAddress[helperAddress]
    if (!helperCode) {
      throw new Error('no helper code configured for address ' + helperAddress)
    }

    helper = {
      address: helperAddress,
      code: helperCode,
    }
  }


  const result = await evmInterpret(
    data.bytecode,
    {
      gasLimit: GAS_LIMIT,
      helper: helper,
      codeAddress: opts.codeAddress,
      chainId: opts.chainId,
    },
    makeStepListener(100, {helperAddress: helperAddress}),
  )

  if (result.exceptionError) {
    throw new Error(result.exceptionError.error)
  }
  onRenderStateChange('INTERPRET_END', {})

  return {
    imageData: new Blob([result.returnValue], {type: 'image/bmp'}),
    gasUsed: result.gasUsed.toString(),
  }
}

