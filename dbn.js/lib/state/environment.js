define(function (require, exports, module) {
  "use strict";

  var producer  = require('lib/state/producer')
    , utils     = require('lib/utils')
    ;

  /**
   * DBNEnvironment
   * maintains the mapping of variables
   * Stacked so can pop, push, locals, etc
   */

  var DBNEnvironment = module.exports = function (options) {
    options = options || {};
    this.parent = options.parent || null;
    this.baseLineNo = options.baseLineNo || -1;
    this._inner = {};
    this._varCount = 0;
  };

  (function() {
    this.copy = function () {
      var newEnv = new DBNEnvironment({parent: this.parent, baseLineNo: this.baseLineNo});
      newEnv._inner = utils.copyDict(this._inner);
      newEnv._varCount = this._varCount;
      return newEnv;
    };

    this.length = function () {
      return this._varCount;
    };

    this.get = function (key, fallback) {
      if (typeof fallback === "undefined") {
        fallback = null;
      }

      if (this._inner.hasOwnProperty(key)) {
        return this._inner[key];
      } else {
        if (this.parent === null) {
          return fallback;
        } else {
          return this.parent.get(key, fallback);
        }
      }
    };

    this._set = function (key, value) {
      if (!this._inner.hasOwnProperty(key)) {
        this._varCount++;
      }
      this._inner[key] = value;
    };

    this.set = producer(function (oldEnv, newEnv, keyOrObject, value) {
      if (typeof keyOrObject === "string") {
        // then we assume we have a key, value
        newEnv._set(keyOrObject, value);
      } else if (typeof keyOrObject === "object") {
        // then its a set of key, value pairs to update
        var keysToSet = Object.getOwnPropertyNames(keyOrObject)
          , key
          ;

        for (var i = 0; i < keysToSet.length; i++) {
          key = keysToSet[i];
          newEnv._set(key, keyOrObject[key]);
        }
      }
    });

    this.unset = producer(function (oldEnv, newEnv, key) {
      if (newEnv._inner.hasOwnProperty(key)) {
        delete newEnv._inner[key];
        newEnv._varCount--;
      }
    });

    this.push = function (baseLineNo) {
      return new DBNEnvironment({
        parent: this
      , baseLineNo: baseLineNo
      });
    };

    this.pop = function () {
      if (this.parent === null) {
        throw new TypeError("Cannot pop an environment without a parent!!");
      } else {
        return this.parent;
      }
    };

  }).call(DBNEnvironment.prototype);

});

