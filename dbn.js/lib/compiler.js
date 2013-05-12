define(function (require, exports, module) {
  "use strict";

  var $ = require('vendor/jquery');

  /**
   * DBNCompiler
   */
  var DBNCompiler = module.exports = function (options) {
    options = options || {};

    this.endpoint = options.endpoint;
  };

  (function () {

    // Raw code --> bytecodes
    this.compile = function (dbnCode, callback) {
      $.ajax({
        url: this.endpoint
      , type: 'POST'
      , data: dbnCode
      , contentType: 'application/x-dbn'
      , dataType: 'json'
      , error: function (xhr, err) { callback(err, xhr) }
      , success: function (data) { callback(null, data) }
      })
    };

  }).call(DBNCompiler.prototype);

});
