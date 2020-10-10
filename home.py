# -*- coding: utf-8 -*-
import os
from flask import Flask, redirect, url_for, render_template, request, session
import json

# Custom libs
from semantic import semantic

semantic = semantic()
# videos = semantic.similarity('Sometimes I feel like screaming')
# answers = semantic.ask('What is the meaning of life')

app = Flask(__name__, template_folder='.', static_folder='')
app.debug = True
app.secret_key = 'Testing, attention please'

@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")

@app.route("/query", methods=['GET'])
def query():
    print(request.args)
    query = request.args.get('query')
    videos = semantic.similarity(query)
    return json.dumps(videos)

@app.route("/question", methods=['GET'])
def question():
    print(request.args)
    question = request.args.get('question')
    answers = semantic.ask(question)
    return json.dumps(answers)

@app.route("/aboutMe")
def me():
    return render_template("about.html")

# @app.route('/test')
# def result():
#     if 'query' in session:
#         query = session['query']
#         return f"<h1>{query}</h1>"
#     else:
#         return 'Not found'


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))