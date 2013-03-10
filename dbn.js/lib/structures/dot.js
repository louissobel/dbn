define(function (require, exports, module) {

  /**
   * DBNDot - encapsulates a dot (with x, y coords)
   *
   * @param{Number} x The x coordinate of the dot
   * @param{Number} y The y coordinate of the dot        
   */
  var DBNDot = module.exports = function (x, y) {
    this.x = x;
    this.y = y;
  };

})
