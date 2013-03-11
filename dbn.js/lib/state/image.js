define(function (require, exports, module) {
  "use strict";

  var producer  = require('lib/state/producer')
    , bmpLib   = require('lib/bmp_lib')
    , utils     = require('lib/utils')
    ;
    
  /**
   * DBNImage
   * Stores the image data
   * This is the place where DBN-format colors (0 --> 100) become real ones
   * Not worrying about ghosting just now
   */
  var DBNImage = module.exports = function (options) {

    this.width = 101;
    this.height = 101;

    options = options || {};

    var create;
    if (typeof options.create === "undefined") {
      create = true;
    } else {
      create = options.create;
    }

    if (create) {
      var color;
      if (typeof options.color === "undefined") {
        // still in DBN mode here (0 - 100 greyscale), which is OK
        color = 0;
      } else {
        color = options.color;
      }

      var clippedColor = utils.clip100(color);
      this._initializeImageData(clippedColor);
    }
  };
  
  (function() {

    this.copy = function () {
      var newImg = new DBNImage({
        create:false
      });

      newImg._image = this._cloneImageData();
      return newImg;
    };

    // define the palette Class Variable using self-invoking function
    this._PALETTE = (function() {
      var palette = [];
      // 101 shades of grey
      // with white first (0 is white)
      for (var l = 0; l < 101; l++) {
        var hex = Math.floor(l/100.0 * 255)
          
          // but we want 255 to be in the 0th slot
          , flippedHex = 255 - hex;

        palette.push([flippedHex, flippedHex, flippedHex]);
      }
      return palette;
    })();

    this._initializeImageData = function (color) {

      // we have a palette, and each element is a numerical index into that palette, which is perfect.
      var image = []
        , i // row
        , j // column
        , r // the row
        ;

      for (i = 0; i < this.height; i++) {
        r = [];
        for (j = 0; j < this.width; j++) {
          r.push(color);
        }
        image.push(r);
      }

      this._image = image;
    };

    this._cloneImageData = function () {
      // returns a deep copy of the image data
      var newImage = []
        , i // row
        , j // column
        , or // the old row
        , nr // the new row
        ;

      for (i = 0; i < this.height; i++) {
        or = this._image[i];
        nr = [];
        for (j = 0; j < this.width; j++) {
          nr.push(or[j]);
        }

        newImage.push(nr);
      }

      return newImage;
    };

    this._dbnxToX = function (x) {
      // Converts DBN x coordinate to image format's.
      return x;
    };

    this._dbnyToY = function (y) {
      // Converts DBN y coordiate to image format's.
      return (this.height - 1) - y;
    };

    this.queryPixel = function (x, y) {

      // Arguments given are DBN type coordinates
      x = this._dbnxToX(x);
      y = this._dbnxToY(y);

      // remember, image is row --> column
      return this._image[y][x];
    };

    this._setPixel = function (x, y, value) {
      // X, Y arguments given are DBN type coordinates
      x = this._dbnxToX(x);
      y = this._dbnyToY(y);

      // If x or y is out of range, fail silently.
      // check x
      if (!utils.inRange(x, 0, this.width - 1)) {
        return false;
      }

      // check y
      if (!utils.inRange(y, 0, this.height - 1)) {
        return false;
      }

      // clip value;
      value = utils.clip100(value);

      // assign it to internal hash.
      // remember, _image is row --> column
      this._image[y][x] = value;
    };

    this.setPixel = producer(function (oldImg, newImg, x, y, value) {
      newImg._setPixel(x, y, value);
    });

    this.setPixels = producer(function (oldImg, newImg, pixelArray) {
      // pixel array is an array of [x, y, value] tuples
      for (var i = 0; i < pixelArray.length; i++) {
        newImg._setPixel.apply(newImg, pixelArray[i]);
      }
    });

    this.dataUri = function() {
      // returns the DATAURI of this thing as a bitmap.
      // relying on bmpLib's internal cacheing for now
      return bmpLib.imageSource(bmpLib.scale(this._image, 3), this._PALETTE);
    };

  }).call(DBNImage.prototype);

});