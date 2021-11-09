import React from 'react';

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
      // clear cached image
      this._img = null
    }
    this.drawCanvas()
  }

  side() {
    return this.props.magnify * 101
  }

  drawCanvas() {
    const context = this.canvas.current.getContext('2d');

    if (!this.props.imageData) {
      context.clearRect(0, 0, this.side(), this.side());
      return
    }

    context.imageSmoothingEnabled = false;
    if (this._img) {
      context.drawImage(this._img, 0, 0, this.side(), this.side())
    } else {
      const url = URL.createObjectURL(this.props.imageData)

      let img = new Image()
      img.onload = function() {
        // once the image is loaded, we're good to free the object URL.
        URL.revokeObjectURL(url)

        // and then cache it
        this._img = img
        context.drawImage(img, 0, 0, this.side(), this.side())
      }.bind(this)

      img.onerror = function(e) {
        console.error("error loading bitmap image", e)
      }
      img.src = url;
    }
  }

  imageMouseOver(e) {
    if (!this.props.onPixelHover) {
      return
    }

    const s = this.side();
    const offsetX = Math.min(s-1, Math.max(e.nativeEvent.offsetX, 0))
    const offsetY = Math.min(s-1, Math.max(e.nativeEvent.offsetY, 0))

    const context = this.canvas.current.getContext('2d');
    var data = context.getImageData(offsetX, offsetY, 1, 1).data;
    
    // we know it's greyscale, so only the first one matters
    const color = data[0]

    this.props.onPixelHover({
      x: Math.floor(offsetX / this.props.magnify),
      y: Math.floor(((s - 1) - offsetY) / this.props.magnify),
      color: this.pixelColorToDBN(color),
    })
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
          "dbn-image-holder "
             + (this.props.onPixelHover ? " crosshairs " : "")
             + (this.props.extraClass || "")
        }
        style={{width: this.side()+"px", height: this.side()+"px"}}
        onMouseMove={this.imageMouseOver.bind(this)}
        onMouseLeave={this.imageMouseOut.bind(this)}
        onClick={this.props.onClick}
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
