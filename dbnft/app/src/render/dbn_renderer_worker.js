import './dbn_renderer_worker_etherjs_workaround'
import {evmAssemble, evmInterpret, linkCode} from './evm_tools'
import helperContractCodeByAddress from './helper_contracts'
import { BN } from 'ethereumjs-util'
import immediate from 'immediate'

const GAS_LIMIT = new BN(0xffffffff)

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

const makeStepListener = function(throttleInterval) {
  var lastCalled = 0;
  return function(step) {
    const now = Date.now();
    if (now - lastCalled > throttleInterval) {

      // We KNOW the Bitmap lives at 0x0180....
      // And that it's 10962 long...
      //
      // We also know that 0x0B in memory is used
      // as flag that the "bitmap is ready"
      var wipImage = null;
      if (step.memory[0x0B]) {
        wipImage = new Blob(
          [step.memory.slice(0x0180, 0x0180 + 10962)],
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


  onRenderStateChange('ASSEMBLE_START', {})
  const linkedAssembly = linkCode(assemblyCode, {
    useHelpers: opts.useHelpers,
  })
  if (opts.verbose) {
    console.log(linkedAssembly)
  }

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
      {gasLimit: GAS_LIMIT, data: Buffer.from([0xDE])},
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
    {gasLimit: GAS_LIMIT, data: Buffer.from([0x33])}
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
    {gasLimit: GAS_LIMIT, helper, codeAddress: opts.codeAddress},
    makeStepListener(100),
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

