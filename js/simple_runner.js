
window.onload = function() {
  /// assumes there is something called ast
  var fresh = new DBNInterpreterState();
  var result = ast.apply(fresh);
  document.getElementById('lala').src = result.image.data_uri();

  window.result = result;
  console.log(result);
}