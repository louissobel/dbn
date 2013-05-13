/*global requirejs, console */

requirejs.config({
  shim: {
    "vendor/jquery": {
      exports: "jQuery"
    }
  }
});

define(function (require) {
  "use strict";

  var $              = require("vendor/jquery")
    , DBNInterpreter = require("dbn.js/lib/interpreter")
    , DBNCompiler    = require("dbn.js/lib/compiler")
    ;

  var compiler = new DBNCompiler({
    endpoint: "/compile"
  });

  var getBytecode = function (cb) {
    var content = $("#script").val();
    return compiler.compile(content, cb);
  };

  var setImage = function (interpreter) {
    $("#lala").attr("src", interpreter.image.dataUri());
  };

  var doDraw = function () {
    getBytecode(function (err, bytecode) {
      if (err) {
        console.log("error!");
      } else {
        var interpreter = new DBNInterpreter(bytecode);
        interpreter.run();
        setImage(interpreter);
      }
    });
  };

  $("document").ready(function () {
    
    $("#do_draw").click(doDraw);
    
  });
  
  
});
