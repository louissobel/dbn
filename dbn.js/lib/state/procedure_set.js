define(function (require, exports, module) {
  "use strict";

  var producer = require('lib/state/producer')
    , utils    = require('lib/utils')
    ;

  /**
   * DBNProcedureSet
   * Object for storing a dictionary of procedures
   * A little janky - there's some hard coded parsing code
   * Such that commands can only be defined in the top stack level
   * So this doesn't have to worry about stacks or anything. 1 per state.
   */
  var DBNProcedureSet = module.exports = function (inner) {
    this._inner = inner || {};
  };

  (function() {

    this.copy = function () {
      var newSet = new DBNProcedureSet();
      newSet._inner = utils.copyDict(this._inner);
      return newSet;
    };

    this.get = function(commandName) {
      if (this._inner.hasOwnProperty(commandName)) {
        return this._inner[commandName];
      } else {
        return null;
      }
    };

    this.add = producer(function(oldSet, newSet, commandName, proc) {
      newSet._inner[commandName] = proc;
    });

  }).call(DBNProcedureSet.prototype);

});


