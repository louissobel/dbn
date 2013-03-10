// assume we have DBNVariable, DBNDot, DBNImage, utils in global namespace.
// not good, but bleh

var RECURSION_LIMIT = 50


var Producer = function(f) {
  var inner = function() {
    // inner will be called in the context of the Thing
    // the Thing must have a copy() method, which will return a copy of it!
    var old_thing = this;
    var new_thing = old_thing.copy()

    // the function will be applied in the context of newThing
    // and the args will be (old, new, *args)
    var retval = f.apply(new_thing, [old_thing, new_thing].concat(Array.prototype.slice.call(arguments)));

    // retval MUST either be the new thing, or undefined
    // this is more an assertion than anything else
    if (!(retval == new_thing || typeof retval == "undefined")) {
      throw new TypeError('Return value of a Producer must either be undefined or the new thing');
    }

    // attach forward and next links if they exist
    if (old_thing.hasOwnProperty('next')) {
      old_thing.next = new_thing;
    }

    if (new_thing.hasOwnProperty('previous')) {
      new_thing.previous = old_thing;
    }

    return new_thing;
  }

  return inner;
}


/**
 * Builtins have to go here. Bleh
 */

// Magic function that builds a built in
var Builtin = function() {
  var formals = Array.prototype.slice.call(arguments);
  var decorator = function(f) {
    var inner = function(state) {
      var args = [];
      formals.forEach(function(formal, index, array) {
        args.push(state.lookup_variable(formal));
      });
      return f.apply(state, args)
    }
    var jsnode = new DBNASTNode({
      type: 'javascript',
      children: [inner]
    });
    var proc = new DBNProcedure(formals, jsnode);
    return proc;
  }
  return decorator;
}


var Line = Builtin('blX', 'blY', 'trX', 'trY')(Producer(function(old_state, new_state, blX, blY, trX, trY) {

  var points = utils.bresenham_line(blX, blY, trX, trY);
  
  var color = old_state.pen_color;

  var pixel_list = [];
  points.forEach(function(tuple, index, array) {
    pixel_list.push([tuple[0], tuple[1], color]);
  });

   new_state.image = old_state.image.set_pixels(pixel_list)

   // GHOSTING STUFF (Python still)
   // current_line_no = new.line_no
   // new_ghosts = (old.ghosts
   //             .add_dimension_line(current_line_no, 1, 'horizontal', blX, blY)  # for blX
   //             .add_dimension_line(current_line_no, 2, 'vertical', blX, blY) # for blY
   //             .add_dimension_line(current_line_no, 3, 'horizontal', trX, trY) # for trX
   //             .add_dimension_line(current_line_no, 4, 'vertical', trX, trY) # for trY
   // )
   // 
   // ## traverse up the environments,
   // ## adding these points to the ghost pointer
   // new_ghosts = new_ghosts.add_points_to_callstack(new.env, 0, points)
   // 
   // new.ghosts = new_ghosts

}));

var Paper = Builtin('value')(Producer(function(old_state, new_state, value) {
  new_state.image = new DBNImage({color: utils.clip_100(value)});
  // clear ghosts?
}));

var Pen = Builtin('value')(Producer(function(old_state, new_state, value) {
  new_state.pen_color = utils.clip_100(value);
}));



/**
 * DBNProcedureSet
 * Object for storing a dictionary of procedures
 * A little janky - there's some hard coded parsing code
 * Such that commands can only be defined in the top stack level
 * So this doesn't have to worry about stacks or anything. 1 per state.
 */
function DBNProcedureSet() {
    this._inner = {
      Line: Line,
      Paper: Paper,
      Pen: Pen
    };
  }

  DBNProcedureSet.prototype.copy = function() {
    var new_set = new DBNProcedureSet();
    new_set._inner = utils.copy_dict(this._inner);
    return new_set;
  }
  
  DBNProcedureSet.prototype.get = function(command_name) {
    if (this._inner.hasOwnProperty(command_name)) {
      return this._inner[command_name];
    } else {
      return null;
    }
  }

  DBNProcedureSet.prototype.add = Producer(function(old_set, new_set, command_name, proc) {
    new_set._inner[command_name] = proc;
  });


/**
 * DBNEnvironment
 * maintains the mapping of variables
 * Stacked so can pop, push, locals, etc
 */

function DBNEnvironment(options) {
    options = options || {};
    this.parent = options.parent || null;
    this.base_line_no = options.base_line_no || -1;
    this._inner = {};
    this._var_count = 0;
  }
  
  DBNEnvironment.prototype.copy = function() {
    new_env = new DBNEnvironment({parent: this.parent, base_line_no: this.base_line_no});
    new_env._inner = utils.copy_dict(this._inner);
    new_env._var_count = this._var_count;
    return new_env;
  }

  DBNEnvironment.prototype.length = function() {
    return this._var_count;
  }

  DBNEnvironment.prototype.get = function(key, fallback) {
    if (typeof fallback == "undefined") {
      fallback = null;
    }

    if (this._inner.hasOwnProperty(key)) {
      return this._inner[key];
    } else {
      if (this.parent == null) {
        return fallback;
      } else {
        return this.parent.get(key, fallback);
      }
    }
  }

  DBNEnvironment.prototype._set = function(key, value) {
    if (!this._inner.hasOwnProperty(key)) {
      this._var_count++;
    }
    this._inner[key] = value;
  }
  
  DBNEnvironment.prototype.set = Producer(function(old_env, new_env, key_or_object, value) {
    if (typeof key_or_object == "string") {
      // then we assume we have a key, value
      new_env._set(key_or_object, value);
    } else if (typeof key_or_object == "object") {
      // then its a set of key, value pairs to update
      Object.getOwnPropertyNames(key_or_object).forEach(function(key, index, array) {
        new_env._set(key, key_or_object[key])
      });
    }
  })
  
  DBNEnvironment.prototype.delete = Producer(function(old_env, new_env, key) {
    if (new_env._inner.hasOwnProperty(key)) {
      delete new_env._inner[key];
      new_env._var_count--;
    }
  })
  
  DBNEnvironment.prototype.push = function(base_line_no) {
    return new DBNEnvironment({parent: this, base_line_no: base_line_no});
  }
  
  DBNEnvironment.prototype.pop = function() {
    if (this.parent == null) {
      throw new TypeError("Cannot pop an environment without a parent!!");
    } else {
      return this.parent;
    }
  }



/**
 * DBNImage
 * Stores the image data
 * This is the place where DBN-format colors (0 --> 100) become real ones
 * Not worrying about ghosting just now
 */
function DBNImage(options) {
    
    this.width = 101;
    this.height = 101;
  
    options = options || {};
  
    var create;
    if (typeof options.create == "undefined") {
      create = true;
    } else {
      create = options.create;
    }
    
    if (create) {
      var color;
      if (typeof options.color == "undefined") {
        color = 0; // still in DBN mode here, which is OK
      } else {
        color = options.color;
      }

      var clipped_color = utils.clip_100(color);
      this._initialize_image_data(clipped_color);
    }    
  }
  
  DBNImage.prototype.copy = function() {
    var new_img = new DBNImage({create:false});
    new_img._image = this._clone_image_data();
    return new_img;
  }

  // define the palette Class Variable using self-invoking function
  DBNImage.prototype._PALETTE = (function() {
    var palette = [];
    // 101 shades of grey
    // with white first (0 is white)
    for (var l=0;l<101;l++) {
      var hex = Math.floor(l/100.0 * 255);
      // but we want 255 to be in the 0th slot
      var flipped_hex = 255 - hex;
      palette.push([flipped_hex, flipped_hex, flipped_hex]);
    }
    return palette
  })();
  
  DBNImage.prototype._initialize_image_data = function(color) {
    // we have a palette, and each element is a numerical index into that palette, which is perfect.
    var image = [];
    var i; // row
    var j; // column
    var r; // the row;
    for (i=0;i<this.height;i++) {
      r = [];
      for (j=0;j<this.width;j++) {
        r.push(color);
      }
      image.push(r);
    }
    this._image = image;
  }

  DBNImage.prototype._clone_image_data = function() {
    // returns a deep copy of the image data
    var new_image = [];
    var i; // row
    var j; // column
    var or; // the old row
    var nr; // the new row
    
    for (i=0;i<this.height;i++) {
      or = this._image[i];
      nr = [];
      for (j=0;j<this.width;j++) {
        nr.push(or[j]);
      }
      new_image.push(nr);
    }
    return new_image;
  }
  
  DBNImage.prototype._dbnx_to_x = function(x) {
    // converts DBN x coordinate to image formats
    return x;
  }
  
  DBNImage.prototype._dbny_to_y = function(y) {
    // converts DBN y coordiate to image formats
    return (this.height - 1) - y;
  }
  
  DBNImage.prototype.query_pixel = function(x, y) {
    // this is x, y in DBN
    x = this._dbnx_to_x(x);
    y = this._dbnx_to_y(y);
    return this._image[y][x] // remember, image is row --> column
  }
  
  DBNImage.prototype._set_pixel = function(x, y, value) {
    // if x or y is out of range, fail silently
    x = this._dbnx_to_x(x);
    y = this._dbny_to_y(y);

    // check x
    if (!utils.in_range(x, 0, this.width - 1)) {
      return false;
    }

    // check y
    if (!utils.in_range(y, 0, this.height - 1)) {
      return false;
    }

    // clip value;
    value = utils.clip_100(value);
    this._image[y][x] = value;
  }

  DBNImage.prototype.set_pixel = Producer(function(old_img, new_img, x, y, value) {
    new_img._set_pixel(x, y, value);
  })

  DBNImage.prototype.set_pixels = Producer(function(old_img, new_img, pixel_array) {
    // pixel array is an array of [x, y, value] tuples
    var array_length = pixel_array.length;
    var i;
    for (i=0;i<array_length;i++) {
      new_img._set_pixel.apply(this, pixel_array[i]);
    }
  })

  DBNImage.prototype.data_uri = function() {
    // returns the DATAURI of this thing as a bitmap.
    // relying on bmp_lib's internal cacheing for now
    return bmp_lib.imageSource(bmp_lib.scale(this._image,3), this._PALETTE);
  }



/**
 * And now, the interpreter state!
 */
function DBNInterpreterState(options) {
    options = options || {};
    
    var create;
    if (typeof options.create == "undefined") {
      create = true;
    } else {
      create = options.create;
    }
    if (create) {
      var initial_paper_color = 0; //dbn color!
      var initial_pen_color = 100; //dbn color!
      
      this.image = new DBNImage({color:initial_paper_color});
      this.pen_color = initial_pen_color;
      this.env = new DBNEnvironment();
      this.commands = new DBNProcedureSet();
      //this.ghosts = new DBNGhosts();
      
      this.stack_depth = 0;
      this.line_no = -1;
    }
    
    // but no matter what, make sure we have next/previous
    // own properties (look in Producer for why that's important!)
    this.next = null;
    this.previous = null;
  }
  
  DBNInterpreterState.prototype.copy = function() {
    var new_state = new DBNInterpreterState({create:false});
    new_state.image = this.image;
    new_state.pen_color = this.pen_color;
    new_state.env = this.env;
    new_state.commands = this.commands;
    new_state.ghosts = this.ghosts;
    
    new_state.stack_depth = this.stack_depth;
    new_state.line_no = this.line_no;
    
    return new_state;
  }
  
  DBNInterpreterState.prototype.lookup_command = function(name) {
    return this.commands.get(name);
  }
  
  DBNInterpreterState.prototype.add_command = Producer(function(old_state, new_state, name, proc) {
    new_state.commands = old_state.commands.add(name, proc);
  })
  
  DBNInterpreterState.prototype.lookup_variable = function(name) {
    return this.env.get(name, 0); // default to 0!
  }
  
  DBNInterpreterState.prototype.set_variable = Producer(function(old_state, new_state, key, value) {
    new_state.env = old_state.env.set(key, value);
  })
  
  DBNInterpreterState.prototype.set_variables = Producer(function(old_state, new_state, key_values) {
    new_state.env = old_state.env.set(key_values);
  })

  // does a Set statement
  // has to be handled specially because well, it's special!
  // (meaning i'm pretty sure i can't shim it as a builtin)
  DBNInterpreterState.prototype.set = Producer(function(old_state, new_state, lval, rval) {
    // lval either DBNDot or Variable or WTF?
    // rval is evaulated, so a number
    
    if (lval instanceof DBNDot) {
      new_state.image = old_state.image.set_pixel(lval.x, lval.y, rval)    
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
      new_state.env = old_state.env.set(lval.name, rval);
    } else {
      throw new TypeError("Unknown lval! " + lval.constructor.name);
    }
  })
  
  DBNInterpreterState.prototype.push = Producer(function(old_state, new_state) {
    if (old_state.stack_depth >= RECURSION_LIMIT) {
      throw new TypeError("Recursion too deep! Limit: " + RECURSION_LIMIT)
    } else {
      new_state.env = old_state.env.push(base_line_no=old_state.line_no);
      new_state.stack_depth = old_state.stack_depth + 1;
    }
  })

  DBNInterpreterState.prototype.pop = Producer(function(old_state, new_state) {
    new_state.env = old_state.env.pop();
    new_state.stack_depth = old_state.stack_depth - 1;
  })
  
  
  DBNInterpreterState.prototype.set_line_no = Producer(function(old_state, new_state, line_no) {
    // assert line_no should never be -1!
    if (line_no == -1) {
      throw new TypeError("HOW LINE_NO -1??");
    }
    new_state.line_no = line_no;
  })
  

// 
// class DBNGhosts:
//     """
//     immutable state object representing ghosts
//     """
//     
//     def __init__(self):
//         self._ghost_hash = {}
//     
//     def __copy__(self):
//         new = DBNGhosts()
//         new._ghost_hash = copy.copy(self._ghost_hash)
//         return new
//     
//     def _make_key(self, line_no, arg_no):
//         return "l%da%d" % (line_no, arg_no)
//     
//     def _get_image(self, line_no, arg_no):
//         key = self._make_key(line_no, arg_no)
//         return self._ghost_hash.get(key)
// 
//     def _set_image(self, line_no, arg_no, dbnimage):
//         key = self._make_key(line_no, arg_no)
//         self._ghost_hash[key] = dbnimage
//         return dbnimage
//         
//     def _add_points(self, line_no, arg_no, points):
//         """
//         points is a list of tuples
//         """
//         image = self._get_image(line_no, arg_no)
//         if image is None:
//             image = DBNImage(color=0, mode='1')  # bitmap mode
//             
//         new_image = image.set_pixels((x, y, 1) for x,y in points)
//         self._set_image(line_no, arg_no, new_image)
//     
//     @Producer
//     def add_points(old, new, line_no, arg_no, points):
//         new._add_points(line_no, arg_no, points)
//     
//     @Producer
//     def add_point(old, new, line_no, arg_no, point):
//         """
//         point is an (x, y) tuple
//         """
//         new._add_points(line_no, arg_no, [point])
//     
//     @Producer
//     def add_dimension_line(old, new, line_no, arg_no, direction, x, y):
//         """
//         adds a dimension line!
//         """
//         points = utils.dimension_line(direction, x, y)
//         new._add_points(line_no, arg_no, points)
//  
//     @Producer
//     def add_points_to_callstack(old, new, walking_env, arg_no, points):
//         while walking_env.parent is not None:
//             line_no = walking_env.base_line_no
//             if line_no == -1:
//                 raise AssertionError("base_line_no of an environment should not be -1 unless it is the root environment")
//             new._add_points(line_no, arg_no, points)
//             walking_env = walking_env.parent
//             
//     @Producer
//     def add_point_to_callstack(old, new, walking_env, arg_no, point):
//         while walking_env.parent is not None:
//             line_no = walking_env.base_line_no
//             if line_no == -1:
//                 raise AssertionError("base_line_no of an environment should not be -1 unless it is the root environment")
//             new._add_points(line_no, arg_no, [point])
//             walking_env = walking_env.parent
