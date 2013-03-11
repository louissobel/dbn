define(function (require, exports, module) {
  "use strict";

  var DBNInterpreterState = require('lib/state/interpreter_state')
    , DBNASTNode          = require('lib/ast_node')
    ;
  
  
  var sendScript = function(script) {
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
      if (xmlhttp.readyState==4 && xmlhttp.status==200) {
        var ast = eval(xmlhttp.responseText);
        if (ast === null) {
          window.alert('tokenize / parse error');
        } else {
          render(ast);
        }
      } 
    };

    xmlhttp.open("POST","/compile", true);
    xmlhttp.setRequestHeader("Content-type","application/x-dbn");
    xmlhttp.send(script);
  };

  var render = function(ast) {
    var fresh = new DBNInterpreterState();
    var result = ast.apply(fresh);
    document.getElementById('lala').src = result.image.dataUri();
    window.result = result;
  };


  window.onload = function() {
    console.log('HI');
    document.getElementById('do_draw').onclick = function() {
      sendScript(document.getElementById('script').value);
    };
  };
  
  
});

