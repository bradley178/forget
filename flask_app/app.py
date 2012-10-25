from flask import Flask
from flask import render_template
from forget.evernote_client import EvernoteClient
from forget.todo.list import List
import os

app = Flask(__name__)

@app.route("/")
def index():
    client = EvernoteClient(file(os.path.expanduser("~/evernote.token")).read())
    list = List(client.note_store, client.authtoken)

    return render_template('index.html', tasks=list.tasks_by_expiration())

if __name__ == "__main__":
    app.run()