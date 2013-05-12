define(function (require, exports, module) {
  "use strict";

  var DBNImage = require('dbn.js/lib/structures/image')
    , DBNFrame = require('dbn.js/lib/structures/frame')
    ;

  var DEFAULT_INITIAL_PEN_COLOR = 100
    , DEFAULT_INITIAL_PAPER_COLOR = 0
    , DEFAULT_VARIABLE_VALUE = 0
    ;

  /**
   * DBNInterpreter
   */
  var DBNInterpreter = module.exports = function (bytecode) {
    this.bytecode = bytecode;

    this.image = new DBNImage({
      color: DEFAULT_INITIAL_PAPER_COLOR
    });

    // Initialize base frame
    var baseFrame = new DBNFrame();
    this.setFrame(baseFrame);

    this.lineNo = -1;
    this.pointer = 0;
    this.terminated = false;
  };

  (function () {

    this.setFrame = function (frame) {
      this.frame = frame;
      this.stack = frame.stack;
    };

    this.run = function () {
      while (!this.terminated) {
        var bytecode = this.bytecode[this.pointer];
        this.step(bytecode.op, bytecode.arg);
      }
    }

    this.step = function (op, arg) {
      var opHandlerName = "_op_" + op
        , opHandler = this[opHandlerName]
        ;

      if (opHandler == null) {
        throw new Error("Unhandled opcode " + opHandlerName);
      }

      opHandler.call(this, arg);
    }

    this._op_END = function (arg) {
      this.terminated = true;
    };

    this._op_SET_LINE_NO = function (arg) {
      var no = parseInt(arg, 10);
      this.lineNo = no;
      this.pointer++;
    };

    this._op_STORE = function (arg) {
      var top = this.stack.pop();
      this.frame.bindVariable(arg, top);
      this.pointer++;
    };

    this._op_LOAD = function (arg) {
      var val = this.frame.lookupVariable(arg, DEFAULT_VARIABLE_VALUE);
      this.stack.push(val);
      this.pointer++;
    };

    this._op_LOAD_INTEGER = function (arg) {
      var val = parseInt(arg, 10);
      this.stack.push(val);
      this.pointer++;
    };

    this._op_LOAD_STRING = function (arg) {
      this.stack.push(arg);
      this.pointer++;
    };

    this._op_SET_DOT = function (arg) {
      var x = this.stack.pop()
        , y = this.stack.pop()
        , val = this.stack.pop()
        ;

      this.image.setPixel(x, y, val);
      this.pointer++;
    };

/*
    LOAD (name):
      push env[name]

    LOAD_INTEGER (n):
      push n

    LOAD_STRING (name):
      push n

    SET_DOT:
      pop
      pop
      pop
      Set [TOP TOP1] TOP2

    GET_DOT:
      pop
      pop
      push [TOP TOP1]

    BINARY_ADD:
      pop
      pop
      push TOP + TOP1

    BINARY_SUB:
      pop
      pop
      push TOP - TOP1

    BINARY_DIV:
      pop
      pop
      push TOP / TOP1

    BINARY_MUL:
      pop
      pop
      push TOP * TOP1

    COMPARE_SAME:
      pop
      pop
      push TOP == TOP1

    COMPARE_SMALLER:
      pop
      pop
      push TOP < TOP1

    DUP_TOPX (x):
      duplicates top x

    POP_TOPX (x):
      pops top x

    ROT_TWO:
      swaps top 2

    JUMP (x):
      jumps to x

    POP_JUMP_IF_FALSE (x):
      pop
      if TOP is false, jumps to x

    POP_JUMP_IF_TRUE (x):
      pop
      if TOP is true, jumps to x

    REPEAT_STEP:
      pop
      pop
      if TOP < TOP1, NEW = TOP + 1
      if TOP > TOP1, NEW = TOP - 1
      push TOP1
      push new

    DEFINE_COMMAND (n):
      makes a command expecting n arguments
      pop
      TOP is address of command body start
      pop
      TOP1 is name of command
      then n more POPs, because n more formal args are expected

    COMMAND (n):
      runs a command!
      pop
      TOP is name of command
      n is number of arguments, pops that many

    LOAD_CODE (path)
      compile and interpret the given file. defined commands and numbers
      should be accessible from the calling file
    */

  }).call(DBNInterpreter.prototype);

});