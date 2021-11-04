import './dbn_renderer_worker_etherjs_workaround'
import {evmAssemble, evmInterpret} from './evm_tools'
import { BN } from 'ethereumjs-util'

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
      lastCalled = now;

      // We KNOW the Bitmap lives at 0x80....
      // And that it's 10962 long...
      //
      // We also know that 0x20 in memory is used
      // as flag that the "bitmap is ready"
      var wipImage = null;
      if (step.memory[0x20]) {      
        wipImage = new Blob(
          [step.memory.slice(0x80, 0x80 + 10962)],
          {type: 'image/bmp'}
        )
      }

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
    }
  }
}

const renderDBN = async function(data, opts, onRenderStateChange) {
  onRenderStateChange('COMPILE_START', {})

  const metadata = {};
  if (data.owningContract) {
    metadata['owning_contract'] = data.owningContract
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
  const bytecode = await evmAssemble(assemblyCode)
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

  const result = await evmInterpret(
    data.bytecode,
    {gasLimit: GAS_LIMIT},
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

