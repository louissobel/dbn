import React from 'react';

class ImageViewer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};

    this.canvas = React.createRef();
  }

  componentDidMount() {
    this.drawCanvas()
  }

  componentDidUpdate() {
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

    const img = new Image()
    const url = URL.createObjectURL(this.props.imageData)
    img.onload = function() {
      context.drawImage(img, 0, 0, this.side(), this.side())
    }.bind(this)
    img.src = url;
  }

  render() {
    return (
      <div className="mx-auto dbn-image-holder" style={{width: this.side()+"px", height: this.side()+"px"}}>
        <canvas ref={this.canvas} width={this.side()} height={this.side()}/>
      </div>
    )
  }

}

export default ImageViewer;
