import flask

#import pydbn

app = flask.Flask(__name__)
app.debug = True


if __name__ == "__main__":
    app.run('0.0.0.0', port=4000)