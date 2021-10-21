import React from 'react';

import Button from 'react-bootstrap/Button';

class ImageViewer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};

    this.canvas = React.createRef();

    this.initializePixelToDBNColorMap()
  }

  componentDidMount() {
    this.drawCanvas()
  }

  componentDidUpdate(prevProps) {
    if (prevProps.imageData !== this.props.imageData) {
      // clear image cache
      this._img = null
    }
    this.drawCanvas()
  }

  side() {
    return this.props.magnify * 101
  }

  drawCanvas() {
    if (!this.props.imageData) {
      return
    }

    const context = this.canvas.current.getContext('2d');
    context.imageSmoothingEnabled = false;

    if (this._img) {
      context.drawImage(this._img, 0, 0, this.side(), this.side())
    } else {
      const url = URL.createObjectURL(this.props.imageData)
      this._img = new Image()
      this._img.onload = function() {
        context.drawImage(this._img, 0, 0, this.side(), this.side())
      }.bind(this)
      this._img.src = url;
    }
  }

  imageMouseOver(e) {
    const s = this.side();
    const offsetX = Math.min(s-1, Math.max(e.nativeEvent.offsetX, 0))
    const offsetY = Math.min(s-1, Math.max(e.nativeEvent.offsetY, 0))

    const context = this.canvas.current.getContext('2d');
    var data = context.getImageData(offsetX, offsetY, 1, 1).data;
    
    // we know it's greyscale, so only the first one matters
    const color = data[0]

    if (this.props.onPixelHover) {
      this.props.onPixelHover({
        x: Math.floor(offsetX / this.props.magnify),
        y: Math.floor(((s - 1) - offsetY) / this.props.magnify),
        color: this.pixelColorToDBN(color),
      })
    }
  }

  imageMouseOut() {
    if (this.props.onPixelHover) {
      this.props.onPixelHover(null);
    }
  }

  render() {
    return (
      <div
        className={
          "mx-auto dbn-image-holder " + (this.props.onPixelHover ? " crosshairs " : "")
        }
        style={{width: this.side()+"px", height: this.side()+"px"}}
        onMouseMove={this.imageMouseOver.bind(this)}
        onMouseLeave={this.imageMouseOut.bind(this)}
      >
        <canvas ref={this.canvas} width={this.side()} height={this.side()}/>
      </div>
    )
  }

  pixelColorToDBN(pixel) {
    return this._pixelToDBNColorMap[pixel]
  }

  initializePixelToDBNColorMap() {
    const pixelColors = [255, 253, 250, 248, 245, 243, 240, 238, 235, 233, 230, 227, 225, 222, 220, 217, 215, 212, 210, 207, 204, 202, 199, 197, 194, 192, 189, 187, 184, 182, 179, 176, 174, 171, 169, 166, 164, 161, 159, 156, 153, 151, 148, 146, 143, 141, 138, 136, 133, 131, 128, 125, 123, 120, 118, 115, 113, 110, 108, 105, 102, 100, 97, 95, 92, 90, 87, 85, 82, 80, 77, 74, 72, 69, 67, 64, 62, 59, 57, 54, 51, 49, 46, 44, 41, 39, 36, 34, 31, 29, 26, 23, 21, 18, 16, 13, 11, 8, 6, 3, 0]
    this._pixelToDBNColorMap = {}
    pixelColors.forEach((v, i) =>
      this._pixelToDBNColorMap[v] = i
    )
  }
}

export default ImageViewer;
