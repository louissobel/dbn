


var send_script = function(script) {
  var xmlhttp = new XMLHttpRequest();
  
  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState==4 && xmlhttp.status==200) {
      eval(xmlhttp.responseText);
      if (ast == null) {
        alert('tokenize / parse error');
      } else {
        render(ast);
      }
    } 
  }

  xmlhttp.open("POST","/compile", true);
  xmlhttp.setRequestHeader("Content-type","application/x-dbn");
  xmlhttp.send(script);
}

var render = function(ast) {
  var fresh = new DBNInterpreterState();
  var result = ast.apply(fresh);
  document.getElementById('lala').src = result.image.data_uri();
}


window.onload = function() {
  document.getElementById('do_draw').onclick = function() {
    send_script(document.getElementById('script').value);
  }
}