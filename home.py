# -*- coding: utf-8 -*-
import os
from flask import Flask, redirect, url_for, render_template, request, session
import json
from threading import Thread

# Custom libs
from semantic import semantic

model = False
semantic = semantic()
videos = semantic.similarity('love meaning') #differences
answers = semantic.ask('what is love?')

app = Flask(__name__, template_folder='.', static_folder='')
app.debug = True
app.secret_key = 'Testing, attention please'

@app.route("/", methods=['GET'])
def home():
    def start_model():
        global model
        if not model:
            model = semantic()
    thread = Thread(target=start_model)
    thread.start()
    return render_template("index.html")

@app.route("/query", methods=['GET'])
def query():
    global model
    if not model:
        model = semantic()
    print(request.args)
    query = request.args.get('query')
    videos = model.similarity(query)
    return json.dumps(videos)

@app.route("/question", methods=['GET'])
def question():
    print(request.args)
    question = request.args.get('question')
    answers = model.ask(question)
    return json.dumps(answers)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))