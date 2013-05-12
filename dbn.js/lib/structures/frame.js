define(function (require, exports, module) {
  "use strict";

  /**
   * DBNFrame
   */
  var DBNFrame = module.exports = function (options) {
    options = options || {};

    this.parent = options.parent || null;
    this.baseLineNo = options.baseLineNo == null ? -1 : options.baseLineNo;
    this.returnPointer = options.returnPointer == null ? -1 : options.returnPointer;
    this.depth = options.depth == null ? 0 : options.depth;

    this.env = {};
    this.stack = [];
  };
  
  (function () {
    this.lookupVariable = function (key, fallback) {
      if (typeof fallback === "undefined") {
        fallback = null;
      }

      if (this.env.hasOwnProperty(key)) {
        return this.env[key];
      } else {
        if (this.parent === null) {
          return fallback;
        } else {
          return this.parent.lookupVariable(key, fallback);
        }
      }
    };

    this.bindVariable = function (keyOrObject, value) {
      if (typeof keyOrObject === "string") {
        // then we assume we have a key, value pair
        this.env[keyOrObject] = value;
      } else if (typeof keyOrObject === "object") {
        // then its a set of key, value pairs to update
        var keysToSet = Object.getOwnPropertyNames(keyOrObject)
          , key
          , i
          ;

        for (i = 0; i < keysToSet.length; i++) {
          key = keysToSet[i];
          this.env[key] = keyOrObject[key];
        }
      }
    };

  }).call(DBNFrame.prototype);

});