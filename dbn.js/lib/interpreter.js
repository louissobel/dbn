define(function (require, exports, module) {
  "use strict";

  var DBNImage = require("dbn.js/lib/structures/image")
    , DBNFrame = require("dbn.js/lib/structures/frame")
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
    this.penColor = DEFAULT_INITIAL_PEN_COLOR;

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
    };

    this.step = function (op, arg) {
      var opHandlerName = "_OP_" + op
        , opHandler = this[opHandlerName]
        ;

      if (opHandler == null) {
        throw new Error("Unhandled opcode " + opHandlerName);
      }

      opHandler.call(this, arg);
    };

    /* opcode handlers */
    this._OP_END = function () {
      this.terminated = true;
    };

    this._OP_SET_LINE_NO = function (arg) {
      var no = parseInt(arg, 10);
      this.lineNo = no;
      this.pointer++;
    };

    this._OP_STORE = function (arg) {
      var top = this.stack.pop();
      this.frame.bindVariable(arg, top);
      this.pointer++;
    };

    this._OP_LOAD = function (arg) {
      var val = this.frame.lookupVariable(arg, DEFAULT_VARIABLE_VALUE);
      this.stack.push(val);
      this.pointer++;
    };

    this._OP_LOAD_INTEGER = function (arg) {
      var val = parseInt(arg, 10);
      this.stack.push(val);
      this.pointer++;
    };

    this._OP_LOAD_STRING = function (arg) {
      this.stack.push(arg);
      this.pointer++;
    };

    this._OP_SET_DOT = function () {
      var x = this.stack.pop()
        , y = this.stack.pop()
        , val = this.stack.pop()
        ;

      this.image.setPixel(x, y, val);
      this.pointer++;
    };

    this._OP_GET_DOT = function () {
      var x = this.stack.pop()
        , y = this.stack.pop()
        , val = this.image.queryPixel(x, y)
        ;
      this.stack.push(val);
      this.pointer++;
    };

    this._OP_BINARY_ADD = function () {
      var top = this.stack.pop()
        , top1 = this.stack.pop()
        , val = top + top1
        ;
      this.stack.push(val);
      this.pointer++;
    };

    this._OP_BINARY_SUB = function () {
      var top = this.stack.pop()
        , top1 = this.stack.pop()
        , val = top - top1
        ;
      this.stack.push(val);
      this.pointer++;
    };

    this._OP_BINARY_MUL = function () {
      var top = this.stack.pop()
        , top1 = this.stack.pop()
        , val = top * top1
        ;
      this.stack.push(val);
      this.pointer++;
    };

    this._OP_BINARY_DIV = function () {
      var top = this.stack.pop()
        , top1 = this.stack.pop()
        ;
      if (top1 === 0) {
        throw new Error("Divide by 0");
      }
      var val = Math.floor(top / top1);
      this.stack.push(val);
      this.pointer++;
    };

    this._OP_COMPARE_SAME = function () {
      var top = this.stack.pop()
        , top1 = this.stack.pop()
        , val = +(top === top1)
        ;
      this.stack.push(val);
      this.pointer++;
    };

    this._OP_COMPARE_SMALLER = function () {
      var top = this.stack.pop()
        , top1 = this.stack.pop()
        , val = +(top < top1)
        ;
      this.stack.push(val);
      this.pointer++;
    };

    this._OP_DUP_TOPX = function (arg) {
      var x = parseInt(arg, 10)
        , dups = this.stack.slice(this.stack.length - x)
        , spliceArgs = [this.stack.length, x].concat(dups)
        ;
      this.stack.splice.apply(this.stack, spliceArgs);
      this.pointer++;
    };

    this._OP_POP_TOPX = function (arg) {
      var x = parseInt(arg, 10);
      this.stack.splice(this.stack.length - x);
      this.pointer++;
    };

    this._OP_ROT_TWO = function () {
      var top = this.stack.pop()
        , top1 = this.stack.pop()
        ;
      this.stack.push(top);
      this.stack.push(top1);
      this.pointer++;
    };

    this._OP_JUMP = function (arg) {
      var target = parseInt(arg, 10);
      this.pointer = target;
    };

    this._OP_POP_JUMP_IF_FALSE = function (arg) {
      var target = parseInt(arg, 10)
        , val = this.stack.pop()
        ;
      if (!val) {
        this.pointer = target;
      } else {
        this.pointer++;
      }
    };

    this._OP_POP_JUMP_IF_TRUE = function (arg) {
      var target = parseInt(arg, 10)
        , val = this.stack.pop()
        ;
      if (val) {
        this.pointer = target;
      } else {
        this.pointer++;
      }
    };

    this._OP_REPEAT_STEP = function () {
      var top = this.stack.pop()
        , top1 = this.stack[this.stack.length - 1]
        , val = top < top1 ? ++top : --top
        ;
      this.stack.push(val);
      this.pointer++;
    };

/*
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