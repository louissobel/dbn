
// eslint-disable-next-line import/no-webpack-loader-syntax
import Worker from 'worker-loader!./dbn_renderer_worker.js'

import frontendEnvironment from '../frontend_environment'

class WorkerPool {
  constructor(max) {
    this.max = max;
    this.inUse = 0;
    this.queue = [];
  }

  async get() {
    return new Promise((resolve) => {
      this.queue.push(resolve)
      console.log('queue length:', this.queue.length)
      this._checkAvailable()
    })
  }

  release() {
    this.inUse--;
    this._checkAvailable();
  }

  _checkAvailable() {
    while (this.inUse < this.max) {
      if (this.queue.length > 0) {
        console.log(this.inUse, this.queue.length, this.max)
        let item = this.queue.shift()
        item(new Worker())
        this.inUse++;
      } else {
        break;
      }
    }
  }
}

const workerPools = {
  gallery: new WorkerPool(10)
}

// String --> bitmapBlob (or error...)
// Emits
const renderDBN = async function(data, onRenderStateChange, cancelSignal) {
  return new Promise(async (resolve, reject) => {

    let worker;
    let release;
    if (data.workerPool) {
      let pool = workerPools[data.workerPool]
      if (!pool) {
        throw new Error('no worker pool ' + data.workerPool)
      }

      worker = await pool.get();
      release = (w) => {
        w.terminate()
        pool.release()
      }
    } else {
      worker = new Worker();
      release = (w) => w.terminate();
    }

    worker.onmessage = (m) => {
      switch (m.data.message) {
        case 'result':
          release(worker)
          resolve(m.data.value)
          break;
        case 'error':
          release(worker)
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
      release(worker)
      reject(e)
    }

    if (cancelSignal) {
      cancelSignal.then(() => {
        console.log('Renderer cancelling')
        release(worker)
        reject({
          type: 'user_cancel',
          message: 'render cancelled'
        })
      })
    }

    data.frontendEnvironment = frontendEnvironment;
    worker.postMessage(data)    
  });
}

export default renderDBN
