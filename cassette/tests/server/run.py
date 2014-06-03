# -*- coding: utf-8 -*-
from flask import Flask, jsonify, redirect, request, url_for

app = Flask(__name__)

IMAGE_FILENAME = "./cassette/tests/server/image.png"


@app.route("/index")
def index():
    return "hello world"


@app.route("/non-ascii-content")
def non_ascii_content():
    return (u"Le Mexicain l'avait achetée en viager "
            u"à un procureur à la retraite. Après trois mois, "
            u"l'accident bête. Une affaire.")


@app.route("/image")
def image():
    with open(IMAGE_FILENAME) as image_handle:
        return image_handle.read()


@app.route("/will_redirect")
def will_redirect():
    return redirect(url_for("redirected"))


@app.route("/redirected")
def redirected():
    return "hello world redirected"


@app.route("/get")
def get():
    return jsonify(args=request.args)


@app.route("/headers")
def headers():
    if request.headers.get("Accept") == "application/json":
        return jsonify(json=True)
    else:
        return "not json"

if __name__ == "__main__":
    app.run()
