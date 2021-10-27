
// eslint-disable-next-line import/no-webpack-loader-syntax
import Worker from 'worker-loader!./dbn_renderer_worker.js'

// TODO: terminate the worker

// String --> bitmapBlob (or error...)
// Emits
const renderDBN = async function(data, onRenderStateChange) {
  return new Promise((resolve, reject) => {
    const worker = new Worker();
    worker.onmessage = (m) => {
      switch (m.data.message) {
        case 'result':
          resolve(m.data.value)
          break;
        case 'error':
          reject(m.data.value)
          break;
        case 'update':
          onRenderStateChange(m.data.value.update, m.data.value.data)
          break;
        default:
          throw new Error(`unhandled message from DBN render worker: ${m}`)
      }
    }

    worker.onerror = (e) => {
      console.error('did not expect error from worker: ', e)
      reject(e)
    }

    worker.postMessage(data)    
  });
}

export default renderDBN
