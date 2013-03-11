define(function (require, exports, module) {
  "use strict";

  var Producer = module.exports = function (f) {

    var inner = function () {
      // inner will be called in the context of the Thing
      // the Thing must have a copy() method, which will return a copy of it!
      var oldThing = this;
      var newThing = oldThing.copy();

      // the function will be applied in the context of newThing
      // and the args will be (old, new, *args)
      var retval = f.apply(newThing, [oldThing, newThing].concat(Array.prototype.slice.call(arguments)));

      // retval MUST either be the new thing, or undefined
      // this is more an assertion than anything else
      if (retval !== newThing && typeof retval !== "undefined") {
        throw new TypeError('Return value of a Producer must either be undefined or the new thing');
      }

      // attach forward and next links if they exist
      if (oldThing.hasOwnProperty('next')) {
        oldThing.next = newThing;
      }

      if (newThing.hasOwnProperty('previous')) {
        newThing.previous = oldThing;
      }

      return newThing;
    };

    return inner;
  };

});

  