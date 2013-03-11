define(function (require, exports, module) {
  "use strict";

  var DBNImage        = require('lib/state/image')
    , DBNEnvironment  = require('lib/state/environment')
    , DBNProcedureSet = require('lib/state/procedure_set')
    , producer        = require('lib/state/producer')
    , DBNDot          = require('lib/structures/dot')
    , DBNVariable     = require('lib/structures/variable')
    ;

  
  var INITIAL_PAPER_COLOR = 0 //dbn color!
    , INITIAL_PEN_COLOR = 100 //dbn color!
    , RECURSION_LIMIT = 50
    ;
  
  /**
   * And now, the interpreter state!
   */
  var DBNInterpreterState = module.exports = function (options) {
    options = options || {};

    var create;
    if (typeof options.create === "undefined") {
      create = true;
    } else {
      create = options.create;
    }

    if (create) {
      this.image = new DBNImage({
        color: INITIAL_PAPER_COLOR
      });

      this.penColor = INITIAL_PEN_COLOR;
      this.env = new DBNEnvironment();
      this.commands = new DBNProcedureSet();
      //this.ghosts = new DBNGhosts();

      this.stackDepth = 0;
      this.lineNo = -1;
    }

    // and no matter what, make sure we have next/previous
    // own properties (look in producer for why that's important!)
    this.next = null;
    this.previous = null;
  }
  
  (function() {

    this.copy = function() {
      var newState = new DBNInterpreterState({
        create: false
      });

      newState.image = this.image;
      newState.penColor = this.penColor;
      newState.env = this.env;
      newState.commands = this.commands;
      //newState.ghosts = this.ghosts;

      newState.stackDepth = this.stackDepth;
      newState.lineNo = this.lineNo;

      return newState;
    };

    this.lookupCommand = function (name) {
      return this.commands.get(name);
    };

    this.addCommand = producer(function (oldState, newState, name, proc) {
      newState.commands = oldState.commands.add(name, proc);
    });

    this.lookupVariable = function (name) {
      // Default value for variable is 0
      return this.env.get(name, 0);
    };

    this.setVariable = producer(function (oldState, newState, key, value) {
      newState.env = oldState.env.set(key, value);
    });

    this.setVariables = producer(function (oldState, newState, keyValues) {
      newState.env = oldState.env.set(keyValues);
    });

    // does a Set statement
    // has to be handled specially because well, it's special!
    // (meaning i'm pretty sure i can't shim it as a builtin)
    this.set = producer(function (oldState, newState, lval, rval) {
      // lval either DBNDot or Variable or WTF?
      // rval is evaulated, so a number

      if (lval instanceof DBNDot) {
        newState.image = oldState.image.setPixel(lval.x, lval.y, rval);    
        // # ghosting stuff (Python still)
        // line_no = new.line_no
        // 
        // new_ghosts = (old.ghosts
        //                 .add_dimension_line(line_no, 1, 'horizontal', x_coord, y_coord)
        //                 .add_dimension_line(line_no, 2, 'vertical', x_coord, y_coord)
        // )
        // new_ghosts = new_ghosts.add_point(line_no, 0, (x_coord, y_coord))
        // new_ghosts = new_ghosts.add_point_to_callstack(new.env, 0, (x_coord, y_coord))
        // new.ghosts = new_ghosts

      } else if (lval instanceof DBNVariable) {
        newState.env = oldState.env.set(lval.name, rval);
      } else {
        throw new TypeError("Unknown lval in set!: " + lval.constructor.name);
      }

    });

    this.push = producer(function (oldState, newState) {

      if (oldState.stackDepth >= RECURSION_LIMIT) {
        throw new TypeError("Recursion too deep! Limit: " + RECURSION_LIMIT);
      } else {
        newState.env = oldState.env.push(oldState.lineNo);
        newState.stackDepth = oldState.stackDepth + 1;
      }

    });

    this.pop = producer(function (oldState, newState) {
      // This will throw error if there is
      // no parent env, so I don't check here
      newState.env = oldState.env.pop();
      newState.stackDepth = oldState.stackDepth - 1;

    });

    this.setLineNo = producer(function (oldState, newState, lineNo) {
      // assert line_no should never be -1!
      if (lineNo === -1) {
        throw new TypeError("HOW LINE_NO -1??");
      }

      newState.lineNo = lineNo;
    });

  }).call(DBNInterpreterState.prototype);

});