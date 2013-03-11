define(function (require, exports, module) {
  "use strict";

  /**
   * DBNProcedure - a class to encapsulate a procedure, its args and its body
   * halfy implements the DBNBaseNode interface, so while its sort of like as AST, it really belongs here
   *
   * @constructor
   * @param{Array<String>} formal_args A list of formal arguments (this will have values bound upon invocation)
   * @param{DBNBaseNode} body A DBNBaseNode that will be applied upon invocation
   */
  var DBNProcedure = module.exports = function (formalArgs, body) {
    this.formalArgs = formalArgs;
    this.argCount = formalArgs.length;
    this.body = body;
    
    // for printing
    this.children = [formalArgs.join(','), this.body];
    this.name = 'proc';
  };

  // (function() {
  // 
  //     this.toString = DBNASTNode.prototype.toString;
  // 
  //   }).call(DBNProcedure.prototype);

});
