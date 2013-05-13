define(function (require, exports, module) {
  "use strict";

  var bmpLib   = require("dbn.js/lib/bmp_lib");

  /**
   * DBNImage
   * Stores the image data
   * This is the place where DBN-format colors (0 --> 100) become real ones
   * Not worrying about ghosting just now
   */
  var DBNImage = module.exports = function (options) {
    options = options || {};

    this.width = 101;
    this.height = 101;

    var color = options.color;
    this.repaper(color);
  };
  
  (function () {

    // define the palette Class Variable using self-invoking function
    this._PALETTE = (function () {
      var palette = [];
      // 101 shades of grey
      // with white first (0 is white)
      for (var l = 0; l < 101; l++) {
        var hex = Math.floor(l / 100.0 * 255)

          // but we want 255 to be in the 0th slot
          , flippedHex = 255 - hex;

        palette.push([flippedHex, flippedHex, flippedHex]);
      }
      return palette;
    })();

    this._initializeImageData = function (color) {

      // we have a palette, and each element is a numerical index into that palette, which is perfect.
      var image = []
        , i // row index
        , j // column index
        , r // the row itself
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

    this._dbnxToX = function (x) {
      // Converts DBN x coordinate to image format's.
      return x;
    };

    this._dbnyToY = function (y) {
      // Converts DBN y coordiate to image format's.
      return (this.height - 1) - y;
    };

    this._checkRange = function (x, y) {
      // Check range
      if (!(x >= 0 && x < this.width)) {
        return false;
      }

      if (!(y >= 0 && y < this.height)) {
        return false;
      }

      return true;
    };

    this.queryPixel = function (x, y) {

      if (!this._checkRange(x, y)) return this.baseColor;

      // Arguments given are DBN type coordinates
      x = this._dbnxToX(x);
      y = this._dbnxToY(y);

      // remember, image is row --> column
      return this._image[y][x];
    };

    this.setPixel = function (x, y, value) {

      if (!this._checkRange(x, y)) return false;

      // X, Y arguments given are DBN type coordinates
      x = this._dbnxToX(x);
      y = this._dbnyToY(y);

      // Clip value
      if (value < 0) value = 0;
      if (value > 100) value = 100;

      // assign it to internal hash.
      // remember, _image is row --> column
      this._image[y][x] = value;
    };

    this.setPixels = function (pixelArray) {
      // pixel array is an array of [x, y, value] tuples
      var i;
      for (i = 0; i < pixelArray.length; i++) {
        this.setPixel.apply(this, pixelArray[i]);
      }
    };

    this.repaper = function (color) {
      this._initializeImageData(color);
      this.baseColor = color;
    };

    this.dataUri = function () {
      // returns the DATAURI of this thing as a bitmap.
      // relying on bmpLib's internal cacheing for now
      return bmpLib.imageSource(bmpLib.scale(this._image, 3), this._PALETTE);
    };

  }).call(DBNImage.prototype);

});