__Ghosting__

 - create immutable state object DBNGhosts
  - internal hash mapping linenumber / argnumber to 101 x 101 bitmap image
  - __copy__ method that copies that internal hash
  - method to add dimension lines to two points at given line, arg
  - method to highlight a dot or dots at given line, arg# I really should clean up interface to image
    - these methods use a DBNImage! (really now just an immutable image)
      to maintain immutability requirements
      * restructure DBNImage a little so that I can make bitmap images with it
 - add two methods to DBNInterpreterState that conditionally delegate to DBNGhosts
   based on current line number / stack depth
   
 - add to the Line builtin dimension lines, line ghost
 - add to Set the dimension lines and dot ghost
 
 - expose it (HAH)