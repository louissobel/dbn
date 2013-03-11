define(function (require, exports, module) {
  "use strict";

  var producer      = require('lib/state/producer')
    , utils         = require('lib/utils')
    , DBNASTNode    = require('lib/ast_node')
    , DBNProcedure  = require('lib/structures/procedure')
    , DBNImage      = require('lib/state/image')
    ;

  // Magic function that builds a built in
  var _builtin = function () {
    var formals = Array.prototype.slice.call(arguments);

    var decorator = function (f) {
      var inner = function (state) {
        var args = [];
        for (var i = 0; i < formals.length; i++) {
          args.push(state.lookupVariable(formals[i]));
        }
        return f.apply(state, args);
      };

      var jsnode = new DBNASTNode({
        type: 'javascript'
      , children: [inner]
      });
      var proc = new DBNProcedure(formals, jsnode);

      return proc;
    };

    return decorator;
  };
  
  module.exports = {

    Line: _builtin('blX', 'blY', 'trX', 'trY')(producer(function (oldState, newState, blX, blY, trX, trY) {

      var points = utils.bresenhamLine(blX, blY, trX, trY)
        , color = oldState.penColor
        , pixelList = []
        , tuple
        ;

      for (var i = 0; i < points.length; i++) {
        tuple = points[i];
        pixelList.push([tuple[0], tuple[1], color]);
      }

      newState.image = oldState.image.setPixels(pixelList);

      // GHOSTING STUFF (Python still)
      // current_line_no = new.line_no
      // new_ghosts = (old.ghosts
      //             .add_dimension_line(current_line_no, 1, 'horizontal', blX, blY)  # for blX
      //             .add_dimension_line(current_line_no, 2, 'vertical', blX, blY) # for blY
      //             .add_dimension_line(current_line_no, 3, 'horizontal', trX, trY) # for trX
      //             .add_dimension_line(current_line_no, 4, 'vertical', trX, trY) # for trY
      // )
      // 
      // ## traverse up the environments,
      // ## adding these points to the ghost pointer
      // new_ghosts = new_ghosts.add_points_to_callstack(new.env, 0, points)
      // 
      // new.ghosts = new_ghosts

    }))
  
  , Paper: _builtin('value')(producer(function (oldState, newState, value) {

      newState.image = new DBNImage({
        color: utils.clip100(value)
      });
      // clear ghosts?

    }))

  , Pen: _builtin('value')(producer(function (oldState, newState, value) {

      newState.penColor = utils.clip100(value);

    }))

  };

});