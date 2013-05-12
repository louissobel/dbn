requirejs.config({
  shim: {
    'vendor/jquery': {
      exports: 'jQuery'
    }
  }
});

define(function (require, exports, module) {
  "use strict";

  var $              = require('vendor/jquery')
    , DBNInterpreter = require('dbn.js/lib/interpreter')
    ;

  var getBytecode = function () {
    var content = $('#script').val()
      , lines   = content.split('\n')
      ;

    var bytecode = []
      , i
      ;

    for (i = 0; i < lines.length; i++) {
      var opAndArg = lines[i].split(' ');
      bytecode.push({
        op: opAndArg[0]
      , arg: opAndArg[1] || null
      });
    }

    return bytecode;
  }

  var setImage = function (interpreter) {
    $('#lala').attr('src', interpreter.image.dataUri());
  }

  var doDraw = function () {
    var bytecode = getBytecode()
      , interpreter = new DBNInterpreter(bytecode)
      ;

    interpreter.run();
    setImage(interpreter);
  }

  $('document').ready(function () {
    
    $('#do_draw').click(doDraw);
    
  });
  
  
});
