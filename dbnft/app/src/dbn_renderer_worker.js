import './dbn_renderer_worker_etherjs_workaround'
import {evmAssemble, evmInterpret} from './evm_tools'

const COMPILE_PATH = '/evm_compile';

onmessage = ({ data }) => {
  try {
    renderDBN(data.code, (s, d) => {
      postMessage({
        message: 'update',
        value: {
          update: s,
          data: d,
        }
      })
    })
    .then((imageData) =>
      postMessage({
        message: 'result',
        value: imageData,
      })
    )
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
          }
        }
      })
    }
  }
}

const renderDBN = async function(code, onRenderStateChange) {
  onRenderStateChange('COMPILE_START', {})

  const response = await fetch(COMPILE_PATH, {
    method: 'POST',
    body: code
  })
  if (!response.ok) {
    throw new Error('Unexpected result: ' + response.status);
  }
  const data = await response.text()
  onRenderStateChange('COMPILE_END', {result: data})


  onRenderStateChange('ASSEMBLE_START', {})
  const bytecode = await evmAssemble(data)
  onRenderStateChange('ASSEMBLE_END', {result: bytecode})

  onRenderStateChange('INTERPRET_START', {})

  const result = await evmInterpret(bytecode, makeStepListener(100))

  if (result.exceptionError) {
    throw new Error(result.exceptionError.error)        
  }
  onRenderStateChange('INTERPRET_END', {})


  return new Blob([result.returnValue], {type: 'image/bmp'})
}
