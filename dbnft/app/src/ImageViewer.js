import React from 'react';

import Navbar from 'react-bootstrap/Navbar';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';

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

  drawCanvas() {
    if (!this.props.imageData) {
      return
    }

    const context = this.canvas.current.getContext('2d');
    context.imageSmoothingEnabled = false;

    const img = new Image()
    const url = URL.createObjectURL(this.props.imageData)
    img.onload = function() {
      context.drawImage(img, 0, 0, 303, 303)
    }.bind(this)
    img.src = url;
  }

  render() {
    return (
      <div className="mx-auto output-holder" style={{width: "303px", height:"303px"}}>
        <canvas ref={this.canvas} width="303" height="303"/>
      </div>
    )
  }

}

export default ImageViewer;
