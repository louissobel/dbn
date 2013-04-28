TODO
======
 
 - clean up ast
   - change name of file
   - move pformat up
  
 - interpreter should not use a else if / else bloop
 - compiler tests (basic but important)
 - interpreter unit tests (one byte code at a time)
 - step method of the interpreter... run is a layer on top of step
 - use the debug mode output in the interpreter consistently
 - shunting yard precedence parsing
 - structure / state module structure
 - add_set_line_no_unless_module decorator
 - settings module (all in one place)
 - bytecodes vs bytecode attribute naming difference between compiler / interpreter
 - make end / start location of ast node return something reasonable
 - move pygmentslexer to inside tokenizer? contrib?