from crypt import methods
from datetime import datetime
from operator import le
from os import getenv

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

import service
from model import Thread, Topic

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = getenv("TRACK_MODIFICATIONS")
app.secret_key = getenv("SECRET_KEY")

db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        username = request.form['username']
        if len(username) < 1:
            flash("Käyttäjätunnus ei voi olla tyhjä!")
            return render_template("register.html")

        pass1 = request.form['password']
        if len(pass1) < 1:
            flash("Salasana ei voi olla tyhjä!")
            return render_template("register.html")

        pass2 = request.form['password2']
        if len(pass2) < 1:
            flash("Salasana ei voi olla tyhjä!")
            return render_template("register.html")

        if pass1 != pass2:
            flash("Salasanat eivät täsmää!", category="error")
            return render_template("register.html")

        admin = False
        if 'isadmin' in request.form:
            admin = True

        user = service.find_user_by_username(username)
        if (user):
            flash(f"Käyttäjätunnus {username} on jo käytössä!")
            return render_template("register.html")

        if not service.register(username, pass1, admin):
            flash("Rekisteröinti epäonnistui!")
            return render_template("register.html")

    return render_template('index.html')


@app.route("/topic", methods=['GET', 'POST'])
def topic():
    topics = []
    if request.method == "GET":
        print("getting all topics..")
        topics = service.get_all_topics()
        print(topics)

    elif request.method == "POST":
        restricted = False
        if 'restricted' in request.form:
            restricted = True

        # remove hardcoded user!
        service.add_topic(Topic(topic_name=request.form['topic'],
                                restricted_access=restricted, created="", created_by=1, updated=""))
        topics = service.get_all_topics()

    return render_template("topics.html", topics=topics)


@app.route("/thread/<int:topic>")
def thread(topic):
    threads = service.get_threads_by_topic(topic)
    print(threads)
    if threads == None:
        threads = []

    return render_template("threads.html", topic_id=topic, threads=threads)


@app.route("/thread", methods=['POST'])
def new_thread():
    topic_id = request.form['topic_id']
    print("ADDNING THREAD TO TOPIC ", topic_id)
    thread_title = request.form['thread']
    print("thread title ", thread_title)

    if len(thread_title) < 1:
        flash("Viestiketjun otsikko ei voi olla tyhjä!")
        return redirect(url_for('thread', topic=topic_id))

    # remove hardcoded user!
    service.add_new_thread(Thread(
        topic_id=topic_id, title=thread_title, created="", created_by=1, updated=""))
    return redirect(url_for('thread', topic=topic_id))


if __name__ == "__main__":
    app.run(debug=True)
