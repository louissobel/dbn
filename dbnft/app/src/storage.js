
class Storage {
  constructor(localOrSession) {
    this.localOrSession = localOrSession

    if (localOrSession === 'local') {
      this.get = function() {
        return window.localStorage
      }
    } else if (localOrSession === 'session') {
      this.get = function() {
        return window.sessionStorage
      }
    } else {
      throw new Error('unknown storage: ' + localOrSession)
    }

    this._check()
  }

  _check() {
    try {
      let testKey = '_____dbnft_storage_test';
      let storage = this.get();
      storage.setItem(testKey, 'ok');
      let echoed = storage.getItem(testKey);

      if (echoed !== 'ok') {
        throw new Error('data did not round trip');
      }
      storage.removeItem(testKey)

      this.enabled = true;
    } catch (e) {
      console.warn(this.localOrSession + ' storage not enabled: ' + e.message)
      this.enabled = false
    }
  }
}

const SessionStorage = new Storage('session')
const LocalStorage = new Storage('local')

export const STORAGE_KEY_RESET_INITIAL_CODE = 'dbnft.io--reset-initial-code';

export {
  SessionStorage,
  LocalStorage,
}

