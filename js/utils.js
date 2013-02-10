// a bunch of pure utility functions

var utils = {
  
  // clips value to be in range [0,100]
  clip_100: function(val) {
    if (val < 0) {
      return 0;
    }
    
    if (val > 100) {
      return 100;
    }
    
    return val;
  },
  
  // returns true if the given number is in the given range
  in_range: function(val, lo, hi) {
    return (val >= lo && val <= hi);
  },
  
  // creates a shallow copy of the given object
  // implicit assumption that it is being used like a HashTable
  copy_dict: function(obj) {
    var props = Object.getOwnPropertyNames(obj);
    var new_obj = {};
    props.forEach(function(prop, index, array) {
      new_obj[prop] = obj[prop];
    });
    return new_obj;
  },
  
  
  // and some drawing utils
  bresenham_line: function(x0, y0, x1, y1) {
    var steep = (Math.abs(y1 - y0) > Math.abs(x1 - x0));
    
    var temp;
    if (steep) {
      temp = x0;
      x0 = y0;
      y0 = temp;

      temp = x1;
      x1 = y1;
      y1 = temp;
    }
    
    var ystep;
    if (y0 < y1) {
      ystep = 1;
    } else {
      ystep = -1;
    }
    
    var points = [];
    var deltax = x1 - x0;
    var deltay = Math.abs(y1 - y0);
    
    var error = -deltax / 2;
    
    var y = y0;
    var x;
    for (x=x0;x<x1+1;x++) {
      if (steep) {
        points.push([y, x]);
      } else {
        points.push([x, y]);
      }
      
      error += deltay;
      if (error > 0) {
        y += ystep;
        error -= deltax
      }
    }
    
    return points; 
  }
  
}