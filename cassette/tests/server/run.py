# -*- coding: utf-8 -*-
from flask import Flask, redirect, url_for, request, jsonify

app = Flask(__name__)


@app.route("/index")
def index():
    return "hello world"


@app.route("/non-ascii-content")
def non_ascii_content():
    return (u"Le Mexicain l'avait achetée en viager "
            u"à un procureur à la retraite. Après trois mois, "
            u"l'accident bête. Une affaire.")


@app.route("/will_redirect")
def will_redirect():
    return redirect(url_for("redirected"))


@app.route("/redirected")
def redirected():
    return "hello world redirected"


@app.route("/get")
def get():
    return jsonify(args=request.args)

if __name__ == "__main__":
    app.run()
